from __future__ import annotations

import gzip
from collections import defaultdict
from math import fabs
from pathlib import Path
from typing import Any
from typing import Callable
from typing import cast
from typing import IO
from typing import Iterator
from typing import Literal
from typing import TypeAlias
from typing import TypedDict

import numpy as np
import pandas as pd
from lxml import etree  # type: ignore

from .logger import logger
from .unimod import Unimod
from .unimod import UnimodLookup

Converters: TypeAlias = dict[str, Callable[[Any], Any]]
FP_UNDERFLOW = np.finfo(np.float32).tiny

# see http://sashimi.sourceforge.net/schema_revision/pepXML/pepXML_v122.xsd

pi = "http://regis-web.systemsbiology.net/pepXML"

# TAGS...
Search_summary = "{%s}search_summary" % pi
Spectrum_query = "{%s}spectrum_query" % pi
Roc_error_data = "{%s}roc_error_data" % pi
File = "File"
MissingPP = "MissingPP"

NSMAP = {"p": pi}


def maybefloat(v: str | None) -> float | None:
    return v if v is None else float(v)


def maybeint(v: str | None) -> int | None:
    return v if v is None else int(v)


def Id(v: Any) -> Any:
    assert v is not None
    return v


def ynToBool(v: str) -> bool:
    return v.upper() == "Y"


def maybeoneZeroToBool(v: str | None) -> None | bool:
    return v if v is None else v == "1"


def tod(D: Converters, node: etree.Element, force: bool = False) -> dict[str, Any]:
    a = node.attrib
    if force:
        return {k: D[k](a[k]) for k in D}
    else:
        return {k: D[k](a[k]) for k in D if k in a}


def name_v(i: list[etree.Element]) -> dict[str, str]:
    return {n.attrib["name"]: n.attrib["value"] for n in i}


def prevent_underflow(v: Any) -> float:
    """These values go to FLOAT columns. Ensure no underflow"""
    v = float(v)
    return 0.0 if fabs(v) < FP_UNDERFLOW else v


COMET = {
    "xcorr": "score1",
    "deltacn": "score2",
    "deltacnstar": "score3",
    "spscore": "score4",
    "sprank": "score5",
    "expect": "score6",
}

MASCOT = {
    "ionscore": "score1",
    "identityscore": "score2",
    "star": "score3",
    "homologyscore": "score4",
    "expect": "score5",  # agh!
}


def chop_spectrum(spectrum: str) -> str:
    # return spectrum.rsplit('.', maxsplit=3)[0]
    ret = ".".join(spectrum.split(".")[:-3])
    return ret


def mods2json(mods: list[dict]) -> list[dict]:
    if not mods:
        return []

    def ml() -> Iterator[dict]:
        for m in mods:
            if "unimod" in m:
                u = m["unimod"]

                yield dict(**m, unimodId=u.unimod_id, mass=u.mono_delta)
            yield m

    return sorted(ml(), key=lambda d: d["position"])


def rowgetters(
    items: dict[str, Any],
    paranoid: bool = False,
) -> Iterator[tuple[str, Callable]]:  # noqa C901:
    def mkget(keys: list[str], check: bool) -> Callable[[Any], Any]:
        *rel, attr = keys

        def func(o: Any) -> Any:
            if check and not o:
                return None
            for k in rel:
                o = o[k]
                if check and not o:
                    return None
            if paranoid and o is None:
                raise RuntimeError(f"none type access for keys {keys} attr {attr}")
            if attr in o:
                return o[attr]
            return None

        return func

    def mkgetm(
        keys: list[list[str]],
        check: bool,
    ) -> Callable[[Any], Any]:  # pragma: no cover
        attr = []
        rel = []
        assert len({len(k) for k in keys}) == 1, keys
        for kl in keys:
            *rl, a = kl
            attr.append(a)
            rel.append(rl)

        def func(o: Any) -> None | list[Any]:
            if check and not o:
                return None
            ol = [o] * len(keys)
            for kv in zip(*rel):
                ol = [o[k] for o, k in zip(o, kv)]
                if check and not all(ol):
                    return None

            return [o[a] for o, a in zip(ol, attr)]

        return func

    def mkfunc(getter: Callable, f: Callable) -> Callable:
        def func(o: Any) -> Any:
            return f(getter(o))

        return func

    def mkfuncm(getter: Callable, f: Callable) -> Callable:
        def func(o: Any) -> Any:
            return f(*getter(o))

        return func

    def noop(val: Any) -> Any:
        return val

    for col, v in items.items():
        if isinstance(v, tuple):
            if len(v) == 3:
                key, cvt, check = v
            else:
                check = False
                key, cvt = v
                if isinstance(cvt, bool):
                    check = cvt
                    cvt = noop
        else:
            key, cvt, check = v, noop, False
        if isinstance(key, tuple):
            yield col, mkfuncm(mkgetm([k.split(",") for k in key], check=check), cvt)
        else:
            yield col, mkfunc(mkget(key.split("."), check=check), cvt)


def modified_peptide(peptide: str, modifications: list[dict[str, Any]]) -> str:
    if not modifications:
        return peptide
    pos = np.array([d["position"] for d in modifications], dtype=np.int32)

    end = len(peptide) + 1
    if pos[0] == 0:
        pos = pos[1:]
    if len(pos) > 0 and pos[-1] == end:
        pos = pos[:-1]
    if len(pos) == 0:
        return peptide
    frags = ["".join(p) for p in np.split(list(peptide), pos)]
    return (
        "".join(f"{f}[{int(m['mass'])}]" for f, m in zip(frags[:-1], modifications))
        + frags[-1]
    )


def spectrum_to_pyteomics_row(  # noqa: C901
    *,
    decoy_prefix: str = "decoy_",
    paranoid: bool = False,
) -> Callable[[dict[str, Any]], Iterator[dict[str, Any]]]:
    # create a pyteomics.pepxml equivalent row
    decoy_prefix = decoy_prefix.lower()

    def is_decoy(accession: str, dprefix: str) -> bool:
        return accession.lower().startswith(dprefix)

    def absolute_delta(v: float) -> float:
        av = fabs(v)
        return 0.0 if av < FP_UNDERFLOW else av

    def first_peptide(modt: list[tuple[str, Any]]) -> str | None:
        for pep, _ in modt:
            return pep
        return None

    GET = dict(
        # run_id=("spectrum.spectrum", sample_mod.run_id),
        # sample_fk=("spectrum.spectrum", sample_mod.sample_fk),
        peptide="hit.peptide",
        # peptideprophet_probability=("hit.peptide_prophet.probability", not expect_pp),
        # interprophet_probability="hit.interprophet.probability",
        # fval=("hit.peptide_prophet.fval", not expect_pp),
        # start_scan_nr="spectrum.start_scan",
        # hit_rank="hit.hit_rank",
        precursor_neutral_mass="spectrum.precursor_neutral_mass",
        calc_neutral_pep_mass="hit.calc_neutral_pep_mass",
        absolute_delta=("hit.massdiff", absolute_delta),
        assumed_charge="spectrum.assumed_charge",
        retention_time_sec="spectrum.retention_time_sec",
        num_missed_cleavages="hit.num_missed_cleavages",
        modifications=(
            "hit.mods",
            lambda modt: mods2json([m for pep, mods in modt for m in mods]),
        ),
        modified_peptide=(
            "hit.mods",
            first_peptide,
        ),  # this is wrong sometimes it show no modifications... see code in pyteomics.pepxml
    )

    getters = dict(rowgetters(GET, paranoid=paranoid))

    # def mapscores(hit):
    #     ret = hit["scores"]
    #     if "xcorr" in ret:
    #         ret["search_engine"] = "Comet"
    #     elif 'ionscore' in ret:
    #         ret["search_engine"] = "Mascot"
    #     return ret

    def row(spectrum: dict[str, Any]) -> Iterator[dict[str, Any]]:
        hits = spectrum["search_hits"]
        for hit in hits:
            if "decoy_prefix" in hit and hit["decoy_prefix"] is not None:
                dprefix = hit["decoy_prefix"].lower()
            else:
                dprefix = decoy_prefix
            decoy_only = all(is_decoy(p["protein"], dprefix) for p in hit["proteins"])
            has_real = any(not is_decoy(p["protein"], dprefix) for p in hit["proteins"])

            o = dict(hit=hit, spectrum=spectrum)
            row = {col: get(o) for col, get in getters.items()}

            row = {**hit, **spectrum, **row}
            row["is_decoy"] = decoy_only
            row["has_real"] = has_real
            # row.update(mapscores(hit))

            row["run"] = chop_spectrum(spectrum["spectrum"])
            proteins = hit["proteins"]

            row["protein_descr"] = [
                d["protein_descr"] if "protein_descr" in d else "" for d in proteins
            ]
            for col in [
                "protein",
                "peptide_prev_aa",
                "peptide_next_aa",
            ]:
                row[col] = [d[col] if col in d else None for d in proteins]
            for col in ["num_tol_term"]:
                row[col] = [d[col] if col in d else -1 for d in proteins]
            if proteins and "num_tot_proteins" in proteins[0]:
                row["num_tot_proteins"] = proteins[0]["num_tot_proteins"]

            if "peptide_prophet" in row:
                pp = row.pop("peptide_prophet")
                if pp is not None:
                    if "all_ntt_prob" in pp:
                        pp["peptideprophet_ntt_prob"] = [
                            float(v) for v in pp.pop("all_ntt_prob")[1:-1].split(",")
                        ]
                    if "probability" in pp:
                        pp["peptideprophet_probability"] = pp.pop("probability")
                    row.update(pp)

            if "interprophet" in row:
                pp = row.pop("interprophet")
                if pp is not None:
                    if "all_ntt_prob" in pp:
                        pp["interprophet_ntt_prob"] = [
                            float(v) for v in pp.pop("all_ntt_prob")[1:-1].split(",")
                        ]
                    if "probability" in pp:
                        pp["interprophet_probability"] = pp.pop("probability")
                    row.update(pp)

            # sheesh!
            if "modified_peptide" not in row or row["modified_peptide"] is None:
                row["modified_peptide"] = row["peptide"]

            if "modifications" in row:
                m = row["modifications"]
                if m and row["peptide"] == row["modified_peptide"]:
                    row["modified_peptide"] = modified_peptide(
                        row["peptide"],
                        row["modifications"],
                    )
            # cleanup
            for col in [
                "scores",
                "mods",
                "isProteinTerm",
                "probability",
                "proteins",
                # "peptide_prophet",
                "search_hits",
                # "retention_time_sec",
                "all_ntt_prob",
            ]:
                row.pop(col, None)
            row["proteins"] = row.pop("protein")
            if "xcorr" in row:
                row["search_engine"] = "Comet"
                row["searchEngineScore"] = row["xcorr"]  # COMET
            elif "ionscore" in row:
                row["search_engine"] = "Mascot"
                row["searchEngineScore"] = row["ionscore"]  # MASCOT
            # elif "expect" in row:
            #     row["search_engine"] = "Unknown"
            #     row["searchEngineScore"] = row["expect"]
            yield row

    return row


def nodes(n: etree.Element) -> str:
    return etree.tostring(n).decode("utf-8")


# pylint: disable=too-many-nested-blocks
def add_unimod_to_mods(
    mods: list[tuple[Any, list[Any]]],
    unimod_lookup: UnimodLookup,
    peptide: str,
    isProteinTerm: Literal["N", "C"] | None,
) -> int:
    nmissing = 0

    def show(uu: list[tuple[Unimod, Any]]) -> str:
        return "{}".format(",".join([str(u.unimod_id) for u, s in uu]))

    for __mod_pep, mod in mods:
        for mm in mod:
            unimods = unimod_lookup.matchModification(
                peptide,
                mm["position"],
                mm.get("massdiff"),
                isProteinTerm,
            )
            if unimods:
                if len(unimods) > 1:
                    # what todo?
                    # iscommon = [t for t in unimods if t[1]]  # any common?
                    # one common match is OK
                    # if len(iscommon) > 1:  # more than one uncommon mod
                    #     click.secho(
                    #         f"multiple (common) unimod matches for {mm} {show(iscommon)}",
                    #         fg="blue",
                    #     )
                    # elif len(iscommon) == 0:
                    #     click.secho(
                    #         f"multiple (uncommon) unimod matches for {mm} {show(unimods)}",
                    #         fg="blue",
                    #     )
                    # else:
                    #     if verbose:
                    #         click.secho(
                    #             f"multiple unimod matches for {mm} {show(unimods)}",
                    #             fg="blue",
                    #         )
                    # choose common
                    unimods = sorted(unimods, key=lambda t: t[1], reverse=True)

                unimod, _iscommon_ = unimods[0]
                mm["unimod"] = unimod  # choose first uncommon
            else:
                # possibly fatal too..
                # click.secho(f"no unimod match for {mm}", fg="red")
                nmissing += 1
    return nmissing


def assertit(val: Any, node: Any) -> None:
    if not val:
        assert val, nodes(node)


class Mod(TypedDict):
    aminoacid: str
    mass: float
    massdiff: float
    variable: bool


class SearchSummary(TypedDict):
    search_engine: str
    mods: list[Mod]
    decoy_prefix: str | None
    mascotParams: list[str] | None


def peptide_maker(  # noqa C901:
    events: Iterator[tuple[Literal["start", "end"], etree.Element]],
    *,
    unimod_lookup: UnimodLookup | None = None,
    search_summary: SearchSummary | None = None,
    use_unimod: bool = True,
) -> Iterator[tuple[str, Any]]:  # noqa: C901
    n_pp_missing = 0

    if unimod_lookup is None:
        unimod_lookup = UnimodLookup([])

    def search_summary_func(n: etree.Element) -> SearchSummary:
        def mods() -> Iterator[Mod]:
            AA: Converters = {
                "aminoacid": Id,
                "mass": float,
                "massdiff": float,
                "variable": ynToBool,
                # 'symbol' : "*"
            }
            for aa in n.xpath(".//p:aminoacid_modification", namespaces=NSMAP):
                yield cast(Mod, tod(AA, aa, force=True))

        params = name_v(n.xpath(".//p:parameter", namespaces=NSMAP))
        decoy_prefix = params.get("decoy_prefix")
        mascotParams_str = params.get("IT_MODS")
        if mascotParams_str is not None:
            mascotParams = [t.strip()[:-4] for t in mascotParams_str.strip().split(",")]
        else:
            mascotParams = None

        return SearchSummary(
            search_engine=n.attrib["search_engine"],  # required
            mods=list(mods()),
            decoy_prefix=decoy_prefix,
            mascotParams=mascotParams,
        )

    def unimodlookup() -> UnimodLookup:
        assert unimod_lookup is not None
        if search_summary is None:
            return unimod_lookup
        known_mods = search_summary["mascotParams"]
        return unimod_lookup.create(known_mods)

    def search_hit(node: etree.Element) -> dict[str, Any]:
        nonlocal n_pp_missing

        PROT: Converters = {
            "protein": Id,
            "protein_descr": lambda t: t,
            "peptide_prev_aa": Id,
            "peptide_next_aa": Id,
            "num_tol_term": int,
            "num_tot_proteins": int,
        }

        def protein(n: etree.Element, force: bool = False) -> dict[str, Any]:
            return tod(PROT, n, force=force)

        proteins = [
            protein(p) for p in node.xpath(".//p:alternative_protein", namespaces=NSMAP)
        ]

        proteins = [protein(node, force=False)] + proteins
        peptide: str = node.attrib["peptide"]
        # nump = proteins[0]["num_tot_proteins"]
        # if not nump == len(proteins):
        #     logger.warning(
        #         "num_tot_proteins mismatch %s %d %d",
        #         peptide,
        #         nump,
        #         len(proteins),
        #     )

        _scores = name_v(node.xpath(".//p:search_score", namespaces=NSMAP))

        SC: dict[str, Callable[[Any], int | float]] = {
            "xcorr": prevent_underflow,
            "deltacn": prevent_underflow,
            "deltacnstar": prevent_underflow,
            "spscore": prevent_underflow,
            "sprank": int,
            "expect": prevent_underflow,
            "ionscore": prevent_underflow,
            "identityscore": prevent_underflow,
            "star": int,
            "homologyscore": prevent_underflow,
            "hyperscore": prevent_underflow,
            "nextscore": prevent_underflow,
        }

        scores = {k: SC[k](_scores[k]) for k in _scores if k in SC}

        def doPP(ret: dict[str, float | str], p: Any, cdict: Converters) -> None:
            for attr in ["probability", "all_ntt_prob"]:
                v = p.attrib[attr]
                ret[attr] = float(v) if attr == "probability" else v
            pp = name_v(
                p.xpath(".//p:search_score_summary/p:parameter", namespaces=NSMAP),
            )

            ret.update({k: cdict[k](pp[k]) for k in cdict if k in pp})

        PP: Converters = {
            "fval": float,
            "ntt": float,
            "nmc": float,
            "massd": float,
            "isomassd": float,
        }  # stored as fval
        pep_prophet: dict[str, float | str] = {}
        for p in node.xpath(
            ".//p:peptideprophet_result",
            namespaces=NSMAP,
        ):
            doPP(pep_prophet, p, PP)

        IP: Converters = {
            "nrs": float,
            "nsi": float,
            "nsm": float,
        }
        interprophet: dict[str, float | str] = {}
        for p in node.xpath(
            ".//p:interprophet_result",
            namespaces=NSMAP,
        ):
            doPP(interprophet, p, IP)

        def modification(
            peptide: str,
            m: etree.Element,
        ) -> tuple[str | None, dict[str, Any]]:
            M: Converters = {
                "mass": float,
                "position": int,
                "static": float,
                "variable": float,
            }
            ret = tod(M, m, force=False)
            if "variable" in ret:
                v = ret["variable"]
                if v is not None:
                    ret["massdiff"] = v
            elif "static" in ret:
                v = ret["static"]
                if v is not None:
                    ret["massdiff"] = v

            mass = ret["mass"]
            assert search_summary is not None
            md = [m["massdiff"] for m in search_summary["mods"] if m["mass"] == mass]
            assert md, (md, mass)
            ret["massdiff"] = md[0]
            pos = ret["position"]
            ret["site"] = peptide[pos - 1]
            p = m.getparent()
            return (
                (
                    p.attrib["modified_peptide"]
                    if "modified_peptide" in p.attrib
                    else None
                ),
                ret,
            )

        modsd: dict[str | None, list[dict[str, Any]]] = defaultdict(list)

        for pep, mod in [
            modification(peptide, m)
            for m in node.xpath(
                ".//p:modification_info/p:mod_aminoacid_mass",
                namespaces=NSMAP,
            )
        ]:
            modsd[pep].append(mod)

        for m in node.xpath(".//p:modification_info", namespaces=NSMAP):
            if "mod_nterm_mass" in m.attrib:
                modsd[m.attrib["modified_peptide"]].append(
                    {"position": 0, "mass": float(m.attrib["mod_nterm_mass"])},
                )
            if "mod_cterm_mass" in m.attrib:
                modsd[m.attrib["modified_peptide"]].append(
                    {
                        "position": 1 + len(peptide),
                        "mass": float(m.attrib["mod_nterm_mass"]),
                    },
                )
        mods = list(modsd.items())
        HIT: Converters = {
            "hit_rank": int,  # stored as hit_rank
            "num_matched_ions": int,
            "num_matched_peptides": int,
            "tot_num_ions": int,
            "calc_neutral_pep_mass": float,  # as theoretical mass ?
            "num_missed_cleavages": int,  # stored as missed_cleavages
            # "is_rejected": maybeoneZeroToBool,
            "massdiff": lambda v: (
                0.0 if v.startswith("+-") else float(v)
            ),  # as abs of absolute_delta
        }

        hit = tod(HIT, node, force=False)  # is_rejected missing

        assert not (
            {"massdiff", "hit_rank", "calc_neutral_pep_mass", "num_missed_cleavages"}
            - set(hit)
        ), (
            hit,
            nodes(node),
        )
        assert search_summary is not None
        prefix = search_summary["decoy_prefix"]

        decoy_prefix = prefix.lower() if prefix else None

        def is_a_decoy(a: str) -> bool:
            if decoy_prefix is None:
                return False
            return a.lower().startswith(decoy_prefix)

        # not trustworthy
        if prefix:
            is_decoy = all(is_a_decoy(p["protein"]) for p in proteins)
        else:
            is_decoy = False

        isProteinTerm: Literal["N", "C"] | None = (
            "N"
            if node.attrib["peptide_prev_aa"] == "-"
            else ("C" if node.attrib["peptide_next_aa"] == "-" else None)
        )

        if mods and use_unimod:
            add_unimod_to_mods(mods, unimodlookup(), peptide, isProteinTerm)

        hit["proteins"] = proteins
        hit["peptide"] = peptide  # stored as sequence
        hit["scores"] = scores
        hit["mods"] = mods
        hit["is_decoy"] = is_decoy
        hit["isProteinTerm"] = isProteinTerm
        hit["peptide_prophet"] = pep_prophet
        hit["interprophet"] = interprophet
        hit["decoy_prefix"] = decoy_prefix
        return hit

    def spectrum(n: etree.Element) -> dict[str, Any]:
        assert search_summary is not None

        hits = [search_hit(s) for s in n.xpath(".//p:search_hit", namespaces=NSMAP)]

        SPECTRUM: Converters = {
            "spectrum": Id,
            "start_scan": int,
            "end_scan": int,
            "precursor_neutral_mass": float,
            "uncalibrated_precursor_neutral_mass": float,
            "assumed_charge": int,  # as charge
            "index": int,
            "retention_time_sec": float,  # as retention_time * 1e-9 i.e. nano seconds
        }

        ret = tod(SPECTRUM, n, force=False)
        ret["search_hits"] = hits
        return ret

    def clear(n: etree.Element) -> None:
        n.clear()
        while n.getprevious() is not None:
            del n.getparent()[0]

    for action, n in events:
        if n.tag == Search_summary and action == "end":
            search_summary = search_summary_func(n)
            yield Search_summary, search_summary
            clear(n)
        elif n.tag == Spectrum_query and action == "end":
            assert search_summary is not None, n.tag
            yield Spectrum_query, spectrum(n)
            clear(n)
    if n_pp_missing:
        yield MissingPP, n_pp_missing


def iter_pepxml_fp(
    fp: IO[bytes],
    *,
    unimod_lookup: UnimodLookup | None = None,
) -> Iterator[tuple[str, Any]]:
    search_summary = None
    # pos = 0
    events = etree.iterparse(fp, events=("end",), huge_tree=True)

    for tag, pg in peptide_maker(
        events,
        unimod_lookup=unimod_lookup,
        search_summary=search_summary,
    ):
        if tag == Search_summary:
            if search_summary is not None:
                if search_summary != pg:
                    logger.warning("pepxml: different search_summary!")
            search_summary = pg
            # print('search summary', search_summary)
        else:
            yield tag, pg


def parse_pepxml(  # pragma: no cover
    pep_xmlfile: Path,
    *,
    unimod_lookup: UnimodLookup | None = None,
    use_unimod: bool = False,
) -> Iterator[tuple[str, Any]]:
    # parser = etree.XMLPullParser(("end",), huge_tree=True)
    # events = parser.read_events()

    def iterfp(
        fp: IO[bytes] | gzip.GzipFile,
        fp_raw: IO[bytes],
    ) -> Iterator[tuple[str, Any]]:
        search_summary = None
        pos = 0
        events = etree.iterparse(fp, events=("end",), huge_tree=True)

        for tag, pg in peptide_maker(
            events,
            unimod_lookup=unimod_lookup,
            search_summary=search_summary,
            use_unimod=use_unimod,
        ):
            if tag == Search_summary:
                if search_summary is not None:
                    if search_summary != pg:
                        logger.warning("different search_summary!")
                search_summary = pg
                # print('search summary', search_summary)
            else:
                yield tag, pg
            cpos = fp_raw.tell()
            yield File, cpos - pos
            pos = cpos
        cpos = fp_raw.tell()
        yield File, cpos - pos
        pos = cpos

    if pep_xmlfile.name.endswith(".gz"):
        with open(pep_xmlfile, "rb") as fpraw, gzip.open(fpraw, "rb") as fp:
            yield from iterfp(fp, fpraw)
    else:
        with open(pep_xmlfile, "rb") as fpraw:
            yield from iterfp(fpraw, fpraw)
    # parser.close()


def pepxml_dataframe(
    pepxml: Path,
    level: int = 0,
    number_of_bg_processes: int = 0,
    with_logger: bool = True,
) -> pd.DataFrame:
    from .config import PEPXML_CHUNKS
    from more_itertools import ichunked
    from .logger import log_iterator
    from .pepxml import scan_spectra

    rowf = spectrum_to_pyteomics_row(paranoid=True)

    def gen() -> Iterator[dict[str, Any]]:
        with open(pepxml, "rb") as fp:
            for tag, d in iter_pepxml_fp(fp):
                if tag == Spectrum_query:
                    row = rowf(d)

                    for d in row:
                        yield d  # first search_hit only
                        break

    if with_logger:
        total = sum(1 for _ in scan_spectra(pepxml))
        it = log_iterator(
            gen(),
            total=total,
            level=level,
            desc=f"{pepxml.name}",
            number_of_bg_processes=number_of_bg_processes,
        )
    else:
        it = gen()
    ret = []
    for chunk in ichunked(it, PEPXML_CHUNKS):
        df = pd.DataFrame(chunk)

        for col in df.columns:
            s = df[col]
            if (
                s.dtype.kind == "f"
                and s.dtype == np.float64
                and col
                not in {
                    "uncalibrated_precursor_neutral_mass",
                    "retention_time_sec",
                    "calc_neutral_pep_mass",
                    "precursor_neutral_mass",
                    "massdiff",
                }
            ):
                df[col] = s.astype(np.float32)
            elif s.dtype == "i" and s.dtype == np.int64 and col != "index":
                df[col] = s.astype(np.int32)
        ret.append(df)
    return pd.concat(ret, axis=0, ignore_index=True)


def okdf(df1: pd.DataFrame, df2: pd.DataFrame) -> None:  # pragma: no cover
    # modified_peptide is wrong...
    df2 = df2.set_index("spectrum")
    df1 = df1.set_index("spectrum")
    A = [
        "protein_descr",
        "modifications",
        "modified_peptide",
        "proteins",
        "num_tol_term",
        "peptide_prev_aa",
        "peptide_next_aa",
        "peptideprophet_ntt_prob",
    ]

    cols = list(set(df1.columns) & set(df2.columns))

    def okarr(s: pd.Series, c: str) -> bool:
        a1 = s[c]
        a2 = s[c + "_o"]
        if len(a1) != len(a2):
            return False
        return all(aa1 == aa2 for aa1, aa2 in zip(a1, a2))

    for c in cols:
        if c in A:
            continue
        v = (df1[c] == df2[c]).all()
        if not v:  # NaNs!
            if c == "is_decoy":
                print(c, False)
                continue
            nna = df1[c].isna().sum() + df2[c].isna().sum()
            if nna > 0:
                if np.nanmax(np.abs(df1[c] - df2[c])) != 0:
                    print(c, v)
            else:
                print(c, False)
    # check arrays
    for c in set(A) - {"modifications"}:
        j = df1[[c]].join(df2[[c]], rsuffix="_o")
        a = j.apply(lambda s: okarr(s, c), axis=1).all()
        if not a:
            print(c, a)

    # check modifications only insofar as mass and position are the same
    def fixmod(dl: list[dict[str, Any]]) -> str:
        n = 6
        return ":".join(f"{d['mass']:.{n}f}@{d['position']}" for d in dl)

    c = "modifications"
    d1 = df1[c].apply(fixmod)
    d2 = df2[c].apply(fixmod)
    if not all(d1 == d2):
        print(c, False)


class ErrorData(TypedDict):
    min_prob: float
    sensitivity: float
    error: float
    num_corr: int
    num_incorr: int


def error_data(node: etree.Element) -> list[ErrorData]:  # pragma: no cover
    ret: list[ErrorData] = []
    for e in node.xpath(".//p:roc_data_point", namespaces=NSMAP):
        args = {
            str(k): int(v) if k.startswith("num_") else float(v)
            for k, v in e.attrib.items()
        }
        ret.append(args)  # type: ignore

    return ret


def iter_roc_fp(  # pragma: no cover
    fp: IO,
) -> list[ErrorData]:
    def clear(n: etree.Element) -> None:
        n.clear()
        while n.getprevious() is not None:
            del n.getparent()[0]

    events = etree.iterparse(fp, events=("end",), huge_tree=True)
    for action, n in events:
        if n.tag == Spectrum_query and action == "end":
            clear(n)
            return []

        elif n.tag == Roc_error_data and action == "end":
            if n.attrib["charge"] == "all":
                return error_data(n)
            clear(n)
    return []


def error_data_dataframe(  # pragma: no cover
    pepxml: Path,
) -> pd.DataFrame:
    with pepxml.open("rb") as fp:
        return pd.DataFrame(iter_roc_fp(fp))
