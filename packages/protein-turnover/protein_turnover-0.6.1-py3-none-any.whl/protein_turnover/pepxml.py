from __future__ import annotations

import logging
import mmap
import re
from collections import Counter
from pathlib import Path
from typing import Callable
from typing import Iterator

import numpy as np
import pandas as pd

from .alt_fit import mk_maxIso
from .jobs import TurnoverJob
from .logger import logger
from .resourcefiles import PepXMLResourceFile
from .types.pepxmltypes import PepXMLRunRow
from .utils import Apply
from .utils import human
from .utils import IO
from .utils import PeptideSettings

# CALL TREE


# get_and_filter_pepxml
# | --- getpepxml
#            | ---- pepxml_create (if no cache)
#                        | --- pepxml_raw # pep.xml to df
#                        | --- pepxml_out # df -> parquet
#                                 | --- IO.write_df
#            | IO.read_df (from cache)
#  | --- filter_pepxml
#         filter X
#              | --- compute_mz_modcol
#                          | --- compute_mz
#
#              | -- compute_maxIso (and mzranges)
#  | --- aggregate_search_hits
#
#
def bchop_spectrum(spectrum: bytes) -> bytes:
    ret = b".".join(spectrum.split(b".")[:-3])
    return ret


SPECTRUM = re.compile(b'spectrum="([^"]+)"')


## @export
def count_spectra(pepxml: Path) -> dict[str, int]:
    """Very fast inspection of pep.xml spectra names"""
    cnt: dict[bytes, int] = Counter()
    with pepxml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for m in SPECTRUM.finditer(mm):
                spectrum = bchop_spectrum(m.group(1))
                cnt[spectrum] += 1

    return {k.decode("ascii"): v for k, v in cnt.items()}


SPECTRUM_QUERY = re.compile(b"<spectrum_query ")


def scan_spectra(pepxml: Path) -> Iterator[int]:
    """Very fast inspection of pep.xml spectra queries"""
    with pepxml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for m in SPECTRUM_QUERY.finditer(mm):
                yield m.start(0)


PEPTIDE_PROPHET_QUERY = re.compile(b"<peptideprophet_summary ")


## @export
def scan_pp_probability(pepxml: Path) -> bool:
    with pepxml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for _ in PEPTIDE_PROPHET_QUERY.finditer(mm):
                return True
    return False  # pragma: no cover


def decoy_prefix_fn(prefix: str = "DECOY_") -> Callable[[list[str]], bool]:
    prefix = prefix.lower()
    return lambda proteins: all(p.lower().startswith(prefix) for p in proteins)


def decoy_postfix_fn(postfix: str = "_DECOY") -> Callable[[list[str]], bool]:
    postfix = postfix.lower()
    return lambda proteins: all(p.lower().endswith(postfix) for p in proteins)


def compute_mz(df: pd.DataFrame) -> pd.DataFrame:
    # add H+
    HPLUS = 1.00727646677
    df["observed_mz"] = df["precursor_neutral_mass"] / df["assumed_charge"] + HPLUS

    df["mz"] = df["calc_neutral_pep_mass"] / df["assumed_charge"] + HPLUS
    return df


def compute_labelledRuns(df: pd.DataFrame, runNames: set[str] | None = None):
    if runNames is not None:
        df["isLabelledRun"] = df["run"].apply(lambda r: r in runNames)
    else:
        df["isLabelledRun"] = False
    return df


def compute_modcol(
    df: pd.DataFrame,
    decoy_prefix: str = "DECOY_",
    decoy_postfix: str | None = None,
) -> pd.DataFrame:
    from .utils import calculate_fdrs

    decoyfn = (
        decoy_postfix_fn(decoy_postfix)
        if decoy_postfix is not None
        else decoy_prefix_fn(decoy_prefix)
    )
    df["modcol"] = df["modifications"].apply(Apply.modcol)
    if "is_decoy" not in df.columns:
        df["is_decoy"] = df["proteins"].apply(decoyfn)
    if "fdr" not in df.columns:
        for prob in ["peptideprophet_probability", "probability"]:
            if prob in df.columns:
                df["fdr"] = calculate_fdrs(df, score=prob)
                break

    return df


def unique_seq(some_list: list[list[str]]) -> list[str]:
    return list({s for lv in some_list for s in lv})


def strlist_to_str(some_list: list[str]) -> str:
    return ":".join(sorted(set(some_list)))


# cols = ['spectrum', 'spectrumNativeID', 'precursor_neutral_mass',
#    'assumed_charge', 'retention_time_sec', 'start_scan', 'end_scan',
#    'index', 'proteins', 'protein_descr', 'peptide_next_aa',
#    'peptide_prev_aa', 'num_tol_term', 'xcorr', 'deltacn', 'deltacnstar',
#    'spscore', 'sprank', 'expect', 'modifications', 'hit_rank', 'peptide',
#    'num_tot_proteins', 'num_matched_ions', 'tot_num_ions',
#    'num_missed_cleavages', 'calc_neutral_pep_mass', 'massdiff',
#    'num_matched_peptides', 'modified_peptide', 'fval', 'ntt', 'nmc',
#    'massd', 'isomassd', 'peptideprophet_probability',
#    'peptideprophet_ntt_prob', 'is_rejected']
AGG = dict(
    calc_neutral_pep_mass="median",
    precursor_neutral_mass="median",
    mz="median",
    observed_mz="median",
    retention_time_sec="median",
    num_missed_cleavages="max",
    peptideprophet_probability="max",
    interprophet_probability="max",
    labelledElementCount="max",
    is_decoy="any",
    agg_count="sum",
    proteins=unique_seq,
    protein_descr=unique_seq,
    modifications="first",
    xcorr="max",  # COMET searchEngineScore
    ionscore="max",  # MASCOT searchEngineScore
    run=strlist_to_str,
    isLabelledRun="any",
    searchEngineScore="max",
    fdr="max",
    # PROTXML ....
    probability="max",
    group_number="nunique",
    percent_coverage="max",
    confidence="max",
    protein_description=unique_seq,
    ngroups="max",
)


def aggregate_search_hits(
    df: pd.DataFrame,
    *,
    settings: PeptideSettings,
) -> pd.DataFrame:
    mztol = settings.mzTolerance

    # use_simple_median = settings.retentionTimeCorrection != "UseInSample"

    df["agg_count"] = 1

    assert "modcol" in df.columns

    keys = ["peptide", "_massint", "assumed_charge", "modcol"]
    df["_massint"] = df["calc_neutral_pep_mass"].apply(lambda m: round(m / (2 * mztol)))
    remove = ["_massint"]

    # only values that exist
    agg = {col: v for col, v in AGG.items() if col in df.columns and col not in keys}
    missing = [col for col in df.columns if col not in agg and col not in keys]
    if missing:
        logger.warning("missing aggregate columns: %s", missing)
        for col in missing:
            agg[col] = "first"
    cols = keys + list(agg)

    g = df[cols].groupby(by=keys, as_index=False)

    ret_df = g.aggregate(agg)

    ret_df = ret_df.drop(columns=remove)
    return ret_df


def pepxml_raw(
    pepxml: PepXMLResourceFile,
    level: int = 0,
    number_of_bg_processes: int = 1,
) -> pd.DataFrame:
    # from .broken_api import PepXMLDataFrame
    from .pepxml_reader import pepxml_dataframe

    logger.info("reading: %s", pepxml.original.name)
    df = pepxml_dataframe(
        pepxml.original,
        level=level,
        number_of_bg_processes=number_of_bg_processes,
    )

    logger.info("done: %s", pepxml.original.name)
    return df


def compute_maxIso(
    df: pd.DataFrame,
    settings: PeptideSettings,
) -> pd.DataFrame:
    def element_count(peptide: str) -> int:
        return settings.getElementCountFromPeptide(peptide)

    max_iso = mk_maxIso(settings)

    def mzranges(pep: PepXMLRunRow) -> np.ndarray:
        return settings.eic_mzranges(pep)

    logger.info(
        "compute_maxIso: adding labelledElementCount, maxIso, mzranges",
    )
    df["labelledElementCount"] = df["peptide"].apply(element_count)
    # get rid of peptides with no labelled Elements
    zero = df["labelledElementCount"] == 0
    anyz = zero.sum()
    if anyz > 0:
        logger.warning("removing %s peptides with no labelled element", anyz)
        df = df[~zero].copy()
    df["maxIso"] = df["peptide"].apply(max_iso)
    # ndarray[maxIso+2,2] of mzmin,mzmax
    df["mzranges"] = df[["maxIso", "assumed_charge", "mz", "observed_mz"]].apply(
        mzranges,
        axis=1,
    )
    logger.info("compute_maxIso: done")
    return df


def getpepxml(
    pepxml: PepXMLResourceFile,
) -> pd.DataFrame:
    if not pepxml.cache_pepxml_ok():
        if not pepxml.exists():
            raise FileNotFoundError(str(pepxml.original))
        logger.info('getpepxml: creating cache "%s"', pepxml.original.name)
        pepxml_create(pepxml)
    assert pepxml.cache_pepxml_ok()
    data = pepxml.cache_pepxml()
    logger.info('getpepxml: reading: "%s"', data.name)
    df = IO(data).read_df()
    return df


def filter_pepxml(df: pd.DataFrame, job: TurnoverJob) -> pd.DataFrame:
    from .filters import PepXMLFilter

    if job.match_runNames:  # pragma: no cover
        n = len(df)
        df = df[df["run"].isin(job.runNames)].copy()
        logger.info('filter_pepxml: run names: "%s" [%d/%d]', job.runNames, len(df), n)

    filter = PepXMLFilter(minProbabilityCutoff=job.settings.minProbabilityCutoff)
    df = filter.filter(df, copy=True)

    return df


def compute_pre_pepxml(pepxml_df: pd.DataFrame, job: TurnoverJob) -> pd.DataFrame:
    pepxml_df = compute_labelledRuns(
        pepxml_df,
        runNames=job.runNames if job.match_runNames else None,
    )
    # needed for grouping
    pepxml_df = compute_modcol(pepxml_df)
    return pepxml_df


def compute_post_pepxml(pepxml_df: pd.DataFrame, job: TurnoverJob) -> pd.DataFrame:
    pepxml_df = compute_mz(pepxml_df)  # add mz and observed_mz

    pepxml_df = compute_maxIso(pepxml_df, job.settings)
    return pepxml_df


def get_and_filter_pepxml(job: TurnoverJob) -> pd.DataFrame:
    files = job.to_resource_files()
    ret = []
    for pepxml in files.pepxmls:
        pepxml_df = getpepxml(pepxml)

        pepxml_df = filter_pepxml(pepxml_df, job)
        ret.append(pepxml_df)
    pepxml_df = pd.concat(ret, axis=0, ignore_index=True)

    pepxml_df = compute_pre_pepxml(pepxml_df, job)
    if job.aggregate_peptides and "agg_count" not in pepxml_df:
        logger.info("aggregating: initial number=%d", len(pepxml_df))
        pepxml_df = aggregate_search_hits(
            pepxml_df,
            settings=job.settings,
        )
        logger.info("aggregating done: final number=%d", len(pepxml_df))
    # compute extra columns after any aggregation
    return compute_post_pepxml(pepxml_df, job)


def pepxml_out(
    df: pd.DataFrame,
    pepxml: PepXMLResourceFile,
) -> None:
    from .utils import IO

    data = pepxml.cache_pepxml()

    if logger.isEnabledFor(logging.INFO):  # pragma: no cover
        if "agg_count" in df.columns:
            logger.info(  # pylint: disable=logging-fstring-interpolation
                f"writing file: {data.name}: total={len(df)} multiple={(df.agg_count > 1).sum()}",
            )
        else:
            logger.info("writing file: %s: total=%s", data.name, len(df))

    # df = dehydrate_pepxml(df)
    assert "mzranges" not in df.columns
    IO(data, df).save_df()

    if logger.isEnabledFor(logging.INFO):  # pragma: no cover
        mem = df.memory_usage(deep=True)
        size = data.stat().st_size
        osize = pepxml.original.stat().st_size
        runs = ",".join(sorted(df.run.unique()))
        logger.info(  # pylint: disable=logging-fstring-interpolation
            f"memory={human(mem.sum())} disk={human(size)} original={human(osize)}: runs={runs}",
        )


def pepxml_create(
    pepxml: PepXMLResourceFile,
    level: int = 0,
    number_of_bg_processes: int = 1,
) -> int:
    df = pepxml_raw(
        pepxml,
        level=level,
        number_of_bg_processes=number_of_bg_processes,
    )
    pepxml_out(df, pepxml)
    return level


def dehydrate_pepxml(df: pd.DataFrame) -> pd.DataFrame:
    if "mzranges" in df.columns:
        df["mzranges"] = df["mzranges"].apply(lambda x: x.flatten())
    return df
