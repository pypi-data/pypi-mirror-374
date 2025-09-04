from __future__ import annotations

import logging
import mmap
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Iterator
from typing import NamedTuple
from typing import overload
from typing import TypedDict

import numpy as np
import pandas as pd
from typing_extensions import override

from .fitenvelopes import FAIL_E_NOEICS
from .fitenvelopes import fitEnvelope
from .jobs import TurnoverJob
from .logger import logger
from .logger import show_log
from .parallel_utils import Task
from .resourcefiles import BaseResourceFile
from .resourcefiles import MzMLResourceFile
from .resourcefiles import MzMLResourceFileLocal
from .resourcefiles import PepXMLResourceFile
from .resourcefiles import ProtXMLResourceFile
from .resourcefiles import ResourceFiles
from .resourcefiles import ResultsResourceFile
from .types.pepxmltypes import PepXMLRunRowRT
from .utils import array_split
from .utils import getsize
from .utils import human
from .utils import IO
from .utils import PeptideSettings


class RTDict(TypedDict):
    retention_time_sec: np.ndarray
    scanindex: np.ndarray
    mzmax: np.ndarray
    mzmin: np.ndarray
    imax: np.ndarray


SPECTRUM_QUERY = re.compile(b"<spectrum ")
CENTRIODED = re.compile(b'accession="MS:1000127"')


## @export
def scan_mzml_spectra(mzml: Path) -> Iterator[int]:
    """Very fast inspection of .mzML spectra queries"""
    with mzml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for m in SPECTRUM_QUERY.finditer(mm):
                yield m.start(0)


def maybe_centroided_spectra(mzml: Path) -> bool:
    """Very fast inspection of .mzML spectra queries"""
    with mzml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for m in CENTRIODED.finditer(mm):
                return True
    return False


class Search(NamedTuple):
    mzmin: float
    mzmax: float
    rtmin: float
    rtmax: float

    def isoverlap(self, other: Search) -> bool:
        dmz = min(self.mzmax, other.mzmax) - max(self.mzmin, other.mzmin)
        if dmz < 0:
            return False
        drt = min(self.rtmax, other.rtmax) - max(self.rtmin, other.rtmin)
        if drt < 0:
            return False
        return True


class ByteOrderError(ValueError):
    pass


def mzi_max_intensity(
    mzi: np.ndarray,
    mzmin: float,
    mzmax: float,
    centroided: bool = True,
) -> float:
    mz, i = mzi[0], mzi[1]
    if mzmin > mz[-1] or mzmax < mz[0]:  # pragma: no cover
        # completly out of range
        return 0.0
    q = (mz <= mzmax) & (mz >= mzmin)
    if q.any():
        return i[q].max()
    # we are wholly *between* two mz points so we linearly interpolate and then find max.
    # *NO* centroided peaks mean voids between peaks are basically zero....
    if centroided:
        return 0.0

    iv = np.interp(np.array([mzmin, mzmax]), mz, i)
    return iv.max()


def zeroi() -> np.ndarray:
    return np.array([], dtype=np.float32).reshape(MZI.SHAPE)


EIC_COLUMNS = ("mzmin", "mzmax", "rtmin", "rtmax")
EIC_COLUMNS2 = ("mzranges", "rtmin", "rtmax")


class MZI:
    SHAPE = (2, -1)

    def __init__(
        self,
        mzmlfile: MzMLResourceFile,
    ):
        self.name = mzmlfile.name
        meta, mapname = mzmlfile.cache_mzml(), mzmlfile.cache_memmap()

        self._mzi = np.memmap(mapname, dtype=np.float32, mode="r")

        if self._mzi[0] != MAGIC_NO:
            raise ByteOrderError(
                f'file "{mapname}" can\'t be read (written with different byteorder)',
            )
        # columns: retention_time_sec', 'scanindex', 'mzmax', 'mzmin', 'imax'
        self.df = IO(meta).read_df()

        scanstart = np.concatenate(  # pylint: disable=unexpected-keyword-arg
            ([1], self.df["scanindex"].to_numpy(dtype=np.int64)[:-1]),
            dtype=np.int64,
        )
        self.df["scanstart"] = scanstart
        mzmax = self.df["mzmax"].max()
        mzmin = self.df["mzmin"].min()
        rtmin = self.df["retention_time_sec"].min()
        rtmax = self.df["retention_time_sec"].max()
        self.search = Search(mzmin, mzmax, rtmin, rtmax)
        self.centroided = True

        self.dino = None
        # dino = mzmlfile.cache_dinosaur()
        # if dino.exists():
        #     self.dino = IO(dino).read_df(columns=["mz", "rtStart", "rtEnd"])
        # else:
        #     self.dino = None

    def __repr__(self) -> str:
        return (
            f"MZI({self.name}[{len(self.df)}],"
            f" mz=[{self.search.mzmin:.2f},{self.search.mzmax:.2f}],"
            f" rt=[{self.search.rtmin:.2f},{self.search.rtmax:.2f}])"
        )

    def mzi_column(self, df: pd.DataFrame | None = None) -> pd.Series:
        if df is None:  # pragma: no cover
            df = self.df
        return df[["scanstart", "scanindex"]].apply(self.mzi_apply, axis=1)

    def mzi(self, scanstart: int, scanindex: int) -> np.ndarray:
        return self._mzi[scanstart:scanindex].reshape(self.SHAPE)

    def mzi_apply(self, row: pd.Series) -> np.ndarray:
        return self.mzi(row["scanstart"], row["scanindex"])

    @classmethod
    def from_mzml_file(
        cls,
        mzmlfile: str | Path,
        cache_dir: str | Path | None = None,
        *,
        quiet: bool = False,
    ) -> MZI:
        res = MzMLResourceFileLocal(mzmlfile, cache_dir=cache_dir)
        if not res.cache_mzml_ok():  # pragma: no cover
            if quiet:
                mzml_create(res)
            else:
                with show_log():
                    mzml_create(res)
        return cls(res)

    @classmethod
    def from_mzi_file(
        cls,
        path: str | Path,
        cache_dir: str | Path | None = None,
    ) -> MZI:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f'"{path}" doesn\'t exist!')
        res = MzMLResourceFileLocal(path, cache_dir=cache_dir)
        return cls(res)

    @classmethod
    def can_read_mzi(cls, mzi: str | Path) -> bool:
        if not Path(mzi).exists():
            return False
        try:
            _mzi = np.memmap(mzi, dtype=np.float32, mode="r")
            return _mzi[0] == MAGIC_NO
        except ValueError:  # pragma: no cover
            return False

    def getEIC(
        self,
        mzrange: np.ndarray,  # float[maxIso+2,2]
        rtmin: float,
        rtmax: float,
        *,
        minrt: int = 0,
    ) -> np.ndarray | None:  # float[maxIso+2,len(rt),2]
        # ensure within boundary
        s = self.search
        if not (
            rtmin >= s.rtmin
            and rtmax <= s.rtmax
            and np.any(mzrange[:, 0] <= s.mzmax)
            and np.any(mzrange[:, 1] >= s.mzmin)
        ):
            return None
        rt = self.df["retention_time_sec"]
        q = (rt >= rtmin) & (rt <= rtmax)
        df = self.df[q]
        if len(df) < minrt:  # pragma: no cover
            return None

        mzi = self.mzi_column(df)
        rt = df["retention_time_sec"]
        out = np.zeros((len(mzrange), len(rt), 2), dtype=np.float32)
        for idx, (mzmin, mzmax) in enumerate(mzrange):
            # xcms foobar! XCMS_STEP = 0.1
            # if XCMS_STEP > 0.0:
            #     mzmin, mzmax = (
            #         floor(mzmin / XCMS_STEP) * XCMS_STEP - XCMS_STEP / 2,
            #         ceil(mzmax / XCMS_STEP) * XCMS_STEP + XCMS_STEP / 2,
            #     )
            outofrange = (df["mzmax"] < mzmin) | (df["mzmin"] > mzmax)
            iz = mzi[outofrange].apply(lambda i: 0.0)
            inz = mzi[~outofrange].apply(
                mzi_max_intensity,
                args=(mzmin, mzmax, self.centroided),
            )
            # stack columns and reset index to rt
            imax = pd.concat(
                [idf for idf in [iz, inz] if len(idf) > 0],
                axis=0,
            ).reindex(index=rt.index)
            # 2 column array [rt, intensity]
            rti = pd.concat([rt, imax], axis=1)
            out[idx, :, :] = rti.to_numpy(dtype=np.float32)

        if out[:, :, 1].max() <= 0.0:  # pragma: no cover
            return None
        return out

    def subset(
        self,
        mzmin: float,
        mzmax: float,
        rtmin: float,
        rtmax: float,
    ) -> pd.DataFrame:
        """data from range mzmin <= mz <= mzmax and rtmin <= retention_time_sec <= rtmax"""
        rt = self.df["retention_time_sec"]
        q = (
            (rt >= rtmin)
            & (rt <= rtmax)
            & (self.df["mzmin"] <= mzmax)
            & (self.df["mzmax"] >= mzmin)
        )
        if q.any():
            return self.df[q]
        return pd.DataFrame({n: [] for n in self.df.columns})

    def _getEIC(
        self,
        mzmin: float,
        mzmax: float,
        rtmin: float,
        rtmax: float,
    ) -> np.ndarray | None:
        if not self.search.isoverlap(Search(mzmin, mzmax, rtmin, rtmax)):
            return None

        rt = self.df["retention_time_sec"]
        q = (rt >= rtmin) & (rt <= rtmax)
        # t = (
        #     (rt >= rtmin)
        #     & (rt <= rtmax)
        #     & (self.df["mzmin"] <= mzmax)
        #     & (self.df["mzmax"] >= mzmin)
        # )
        if q.sum() == 0:
            return None

        filtered_df = self.df[q]

        def toimax(row: pd.Series) -> float:
            return mzi_max_intensity(self.mzi_apply(row), mzmin, mzmax, self.centroided)

        imax = filtered_df[["scanstart", "scanindex"]].apply(
            toimax,
            axis=1,
        )

        if imax.max() <= 0.0:  # pragma: no cover
            return None

        rti = pd.concat([filtered_df["retention_time_sec"], imax], axis=1)
        # array will be in column major 'F' order so
        # that transpose will be ok
        return rti.to_numpy(dtype=np.float32)

    def imax(self, df: pd.DataFrame, mzmin: float, mzmax: float) -> np.ndarray:
        df = df[["scanstart", "scanindex"]]
        imax = []
        for r in df.itertuples():
            mz, i = self.mzi(r.scanstart, r.scanindex)  # type: ignore
            q = (mzmin <= mz) & (mzmax >= mz)
            if q.any():
                m = i[q].max()
                imax.append(m)
            else:
                if self.centroided:
                    m = 0.0
                else:
                    m = np.interp(np.array([mzmin, mzmax]), mz, i).max()
                imax.append(m)

        return np.array(imax, dtype=np.float32)

    def eics_from_df(
        self,
        df: pd.DataFrame,
        columns: list[str] | None = None,
        *,
        zero_length: bool = False,
    ) -> pd.Series:
        if columns:
            df = df.rename(
                columns=dict(zip(columns, EIC_COLUMNS)),
            )

        mzmin, mzmax, rtmin, rtmax = EIC_COLUMNS
        _getEIC = self._getEIC

        def findeic(row: pd.Series) -> np.ndarray | float:
            ret = _getEIC(row[mzmin], row[mzmax], row[rtmin], row[rtmax])
            if ret is None:
                return zeroi() if zero_length else np.nan
            return ret.T

        return df[list(EIC_COLUMNS)].apply(findeic, axis=1)

    def eics_from_mzrange_df(
        self,
        df: pd.DataFrame,
        columns: list[str] | None = None,
        *,
        zero_length: bool = False,
    ) -> pd.Series:
        if columns:
            df = df.rename(
                columns=dict(zip(columns, EIC_COLUMNS2)),
            )
        mzranges, rtmin, rtmax = EIC_COLUMNS2
        _getEIC = self.getEIC

        def findeic(row: pd.Series) -> np.ndarray | float:
            ret = _getEIC(row[mzranges], row[rtmin], row[rtmax])
            if ret is None:
                return zeroi().reshape((-1, 0, 2)) if zero_length else np.nan
            return ret

        return df[list(EIC_COLUMNS2)].apply(findeic, axis=1)

    @classmethod
    def dehydrate_eics(cls, s: pd.Series) -> pd.Series:
        def f(a: Any) -> Any:
            return a.flatten() if isinstance(a, np.ndarray) else a

        return s.apply(f)

    @classmethod
    def rehydrate_eics(cls, s: pd.Series) -> pd.Series:
        def f(a: Any) -> Any:
            return a.reshape(cls.SHAPE) if isinstance(a, np.ndarray) else a

        return s.apply(f)

    def __len__(self) -> int:
        return len(self.df)

    @overload
    def __getitem__(self, idx: int) -> np.ndarray: ...

    @overload
    def __getitem__(self, idx: slice) -> pd.Series: ...

    @overload
    def __getitem__(self, idx: list[int]) -> pd.Series: ...

    def __getitem__(self, idx: int | list[int] | slice) -> np.ndarray | pd.Series:
        df = self.df[["scanstart", "scanindex"]].iloc[idx]
        if isinstance(idx, int):
            scanstart: int
            scanindex: int
            scanstart, scanindex = df  # type: ignore
            return self.mzi(scanstart, scanindex)

        return df.apply(self.mzi_apply, axis=1)  # type: ignore


# number must survive roundtrip....
# struct.unpack("f", struct.pack("f", MAGIC_NO))[0] == MAGIC_NO
MAGIC_NO = -0.1234000027179718
# MAGIC_BYTES = b'$\xb9\xfc\xbd'
MAGIC_BYTES = np.array([MAGIC_NO], dtype=np.float32).tobytes()


def mzml_create(
    mzml: MzMLResourceFile,
    level: int = 0,
    number_of_bg_processes: int = 1,
    *,
    ensure_centroided: bool = False,
) -> int:
    """Create cache files for a mzML file"""
    from pymzml.spec import Spectrum, Chromatogram
    from .broken_api import PyMzMLReader
    from .logger import log_iterator

    mzreader = PyMzMLReader(
        mzml.original,
        build_index_from_scratch=False,
    )
    total = mzreader.get_spectrum_count()

    rt_dict = RTDict(
        retention_time_sec=np.zeros(total, dtype=np.float32),
        scanindex=np.zeros(total, dtype=np.int64),
        mzmin=np.zeros(total, dtype=np.float32),
        mzmax=np.zeros(total, dtype=np.float32),
        imax=np.zeros(total, dtype=np.float32),
    )
    n = 0
    scanindex = 1  # first part is a magic number
    mname = mzml.cache_memmap()

    mzml.ensure_cache_dir()

    with mname.open("wb") as fp:
        it: Iterator[Spectrum | Chromatogram] = log_iterator(
            mzreader,
            total=total,
            desc=mzml.original.name,
            level=level,
            number_of_bg_processes=number_of_bg_processes,
        )

        fp.write(MAGIC_BYTES)
        mz: np.ndarray
        i: np.ndarray
        # loop over <spectrumList count="nnnn"><spectrum>....</spectrum>... </spectrumList>

        for spectrum in it:
            # <cvParam cvRef="MS" accession="MS:1000511" name="ms level" value="1"/>
            assert isinstance(spectrum, Spectrum)
            if spectrum.ms_level == 1:
                # <cvParam cvRef="MS" accession="MS:1000016" name="scan start time" value="0.001483586933"
                #       unitCvRef="UO" unitAccession="UO:0000031" unitName="minute"/>

                if ensure_centroided:
                    centroided = spectrum.get("MS:1000127")
                    if not centroided:
                        raise ValueError("expecting centroided spectra!")
                stm = spectrum.scan_time_in_minutes()
                assert isinstance(stm, float)
                rt = stm * 60.0
                mz, i = spectrum.mz, spectrum.i
                mzi = np.vstack((mz, i))
                # mz first, intensity second
                data = mzi.flatten().astype(np.float32)  # .tobytes()
                scanindex += len(data)
                # we will use these to search for suitable rt,mz from pep.xml files
                rt_dict["retention_time_sec"][n] = rt
                rt_dict["mzmax"][n] = mz.max()
                rt_dict["mzmin"][n] = mz.min()

                rt_dict["imax"][n] = i.max()
                rt_dict["scanindex"][n] = scanindex
                n += 1
                fp.write(data.tobytes())

    df = pd.DataFrame({k: v[:n] for k, v in rt_dict.items()})  # type: ignore
    df.sort_values(by="retention_time_sec", inplace=True)
    df.reset_index(drop=True, inplace=True)

    mzml_out(mzml, df)

    from .dinosaur.dinosaur import mzml_dinosaur

    mzml_dinosaur(mzml)

    return level


def getmzml(mzml: MzMLResourceFile) -> MZI:
    if not mzml.cache_ok():
        mzml_create(mzml)
        assert mzml.cache_ok()
    return MZI(mzml)


def mzml_out(
    mzml: MzMLResourceFile,
    df: pd.DataFrame,
) -> None:
    out = mzml.cache_mzml()
    IO(out, df).save_df()

    if logger.isEnabledFor(logging.INFO):  # pragma: no cover
        mname = mzml.cache_memmap()
        mem = df.memory_usage(deep=True).sum()
        g = getsize
        msg = (
            f"written: {mzml.original.name} -> {out.name}: memory={human(mem)} ondisk={human(g(out))},"
            f" mzimap={human(g(mname))} original={human(g(mzml.original))}"
        )
        logger.info(msg)


def dfinfo(df: pd.DataFrame, mzml: MzMLResourceFile, out: Path) -> None:
    if logger.isEnabledFor(logging.INFO):
        mem = df.memory_usage(deep=True).sum()
        g = getsize
        ret = f"{out.name}: memory={human(mem)} ondisk={human(g(out))} original={human(g(mzml.original))}"
        logger.info(ret)


def dehydrate_eics(df: pd.DataFrame) -> pd.DataFrame:
    df["eics_shape"] = df["eics"].apply(lambda a: a.shape)
    df["eics"] = df["eics"].apply(lambda e: e.flatten())
    return df


def turnover_run(
    job: TurnoverJob,
    jobrun: ResultsResourceFile,
    *,
    workers: int = 4,
    save_subset: bool = True,
    nspectra: int | None = None,
    cleanup: bool = True,
    save_job: bool = False,
    testing: int | None = None,
) -> None:
    from .pepxml import get_and_filter_pepxml, dehydrate_pepxml
    from .utils import human, rmfiles
    from .parallel_utils import parallel_tasks

    start = datetime.now()
    pepxml_df = get_and_filter_pepxml(job)

    tasks = create_mz_tasks(pepxml_df, job, nspectra=nspectra, testing=testing)
    if logger.isEnabledFor(logging.INFO):
        taskmem = sum(t.mem() for t in tasks)
        mem = pepxml_df.memory_usage(deep=True).sum()
        info = f"pepxml memory={human(mem)}, tasks[{len(tasks)}/{workers}] total memory=[{human(taskmem)}]"
        logger.info(info)
    # save
    if save_subset:
        pepxml_df = pd.concat(
            [pepxml_df.loc[task.pepxml_df.index] for task in tasks],
            axis="index",
        )
        pepxml_df.index.name = "pepxml_index"
        pepxml_df = pepxml_df.reset_index()
    pepxml_df_filename = jobrun.cache_pepxml()
    pepxml_df = dehydrate_pepxml(pepxml_df)  # dehydrage the mzranges
    IO(pepxml_df_filename, pepxml_df).save_df()
    pepxml_df = None
    # get mzml tasks
    envelopes: list[Path] = []

    ntotal = len(tasks)
    try:
        for idx, (df, mzml) in enumerate(parallel_tasks(tasks, workers=workers), 1):
            logger.info(
                "EIC[%s] task done[%d/%d]: %s[%d]",
                jobrun.original.name,
                idx,
                ntotal,
                mzml.original.name,
                len(df),
            )
            if len(df) == 0:  # pragma: no cover
                continue

            eicsfile = jobrun.cache_partial_envelope(idx)
            df = dehydrate_eics(df)
            IO(eicsfile, df).save_df()
            envelopes.append(eicsfile)

            dfinfo(df, mzml, eicsfile)

        save_result(
            jobrun.cache_result(),
            pepxml_df_filename,
            job.to_resource_files().protxml,
            envelopes,
        )
        if save_job:
            toml = jobrun.cache_result().with_suffix(".toml")
            job.save_file(toml)
        logger.info("turnover finished! %s after %s", job.jobid, datetime.now() - start)
    finally:
        if cleanup:
            envelopes.append(pepxml_df_filename)
            rmfiles(envelopes)


def save_result(
    result_name: Path,
    pepdf: Path,
    protdf: ProtXMLResourceFile,
    envelopes: list[Path],
) -> None:
    from .sqla.model import save_to_file
    from .protxml import getprotxml

    logger.info("consolidating eics")
    eic = consolidate_eic(envelopes)
    eic = eic.set_index("peptide_index")

    me = IO(pepdf).read_df()
    prot = getprotxml(protdf)
    n = len(me)
    if "pepxml_index" in me.columns:  # in save subset
        me = me.set_index("pepxml_index")
    me = me.join(eic, how="inner", rsuffix="_env")
    me = me.reset_index(drop=True)
    if "peptide_env" in me.columns:
        assert (me["peptide"] == me["peptide_env"]).all()
        me.drop(columns=["peptide_env"], inplace=True)
    # create explicit index for parquet
    me.index.name = "result_index"
    me.reset_index(inplace=True)  # add result_index to columns

    logger.info(
        "writing results: %s[%d] original length=%d",
        result_name.name,
        len(me),
        n,
    )
    me = dedup_peptides(me)
    save_to_file(result_name, me, prot)


# def dedup_peptides1(pep: pd.DataFrame) -> pd.DataFrame:
#     return (
#         pep.groupby(by=["peptide", "modcol"])
#         .apply(lambda x: x.sort_values(by="heavyCor", ascending=False).head(1))
#         .reset_index(drop=True)
#     )


def dedup_peptides(pep: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate peptide/modcol rows, taking smallest nnls_residual."""
    return (
        pep.sort_values(by="nnls_residual", ascending=True)
        .groupby(by=["peptide", "modcol", "assumed_charge"])
        .head(1)
        .reset_index()
    )


def consolidate_eic(eicfiles: list[Path]) -> pd.DataFrame:
    df = pd.concat(
        [IO(eic).read_df() for eic in eicfiles],
        axis="index",
        ignore_index=True,
    )
    return df


class MzMLTask(Task):
    @override
    def task_run(self) -> pd.DataFrame:
        mzmlc = MZI(self.mzml)
        done = mzml_calc_mzml_envelopes(
            self.pepxml_df,
            mzmlc,
            self.settings,
            level=self.level,
            number_of_bg_processes=self.number_of_bg_processes,
        )

        outdf = pd.DataFrame(done)
        for col in ["relativeIsotopeAbundance", "enrichment", "heavyCor"]:
            if col in outdf.columns:
                outdf[col] = outdf[col].astype(np.float32)
        return outdf


def create_mz_tasks(
    pepxml_df: pd.DataFrame,
    job: TurnoverJob,
    nspectra: int | None = None,  # spectra chunk sizes for tasks
    *,
    testing: int | None = None,
) -> list[MzMLTask]:
    tasks = []
    mz2run = job.get_mzfile_to_run()
    files = job.to_resource_files()
    todo: list[tuple[pd.DataFrame, MzMLResourceFile]] = []
    dfs: list[tuple[pd.DataFrame, MzMLResourceFile]]

    if testing is not None:
        logger.warning("TESTING has been set to ON! Output files are VOID!")
        pepxml_df = pepxml_df.iloc[:testing]
        nspectra = max(testing // 3, 2)

    for mzml in files.mzmlfiles:
        if job.match_runNames:
            df = pepxml_df[pepxml_df["run"] == mz2run[mzml.name]]
        else:
            df = pepxml_df

        if len(df) == 0:  # pragma: no cover
            continue
        # Don't need "peptide" really... just for sanity check
        df = df[
            [
                "retention_time_sec",
                "peptide",
                "maxIso",
                "mzranges",
                "isLabelledRun",
            ]
        ]
        if nspectra is not None and nspectra > 0:
            chunk_num = max(len(df) // nspectra, 1)
            if chunk_num > 1:
                dfs = [(sdf, mzml) for sdf in array_split(df, chunk_num)]
            else:
                dfs = [(df, mzml)]
        else:
            dfs = [(df, mzml)]
        todo.extend(dfs)

    ntotal = len(todo)
    tasks = [
        MzMLTask(cdf, mzml, job.settings, level, ntotal)
        for level, (cdf, mzml) in enumerate(todo, start=1)
    ]

    return tasks


def calc_rtranges(
    rundf: pd.DataFrame,
    mzmlc: MZI,
    settings: PeptideSettings,
    rt_min: int,
) -> pd.DataFrame:
    rt = mzmlc.df["retention_time_sec"]
    if mzmlc.dino is not None:  # pragma: no cover
        rundf = rundf.join(findrt_dino(mzmlc.dino, rundf, rt, settings))
        rrt = rundf.rtmax - rundf.rtmin
        logger.info("dinosaur: rt range %s-%s secs", str(rrt.min()), str(rrt.max()))
    else:
        rundf = rundf.join(findrt(rundf, rt, settings))

    search = mzmlc.search

    def inrange(mzr) -> np.bool:
        return np.any(mzr[:, 0] <= search.mzmax) and np.any(mzr[:, 1] >= search.mzmin)

    q = (
        (rundf["rtmin"] <= search.rtmax)
        & (rundf["rtmax"] >= search.rtmin)
        & (rundf["rt_count"] >= rt_min)
        & rundf["mzranges"].apply(inrange)  # type: ignore
    )

    return rundf[q]


def compute_rt(rundf: pd.DataFrame, settings: PeptideSettings):
    # if 'rtmin' in rundf.columns or 'rtmax' in rundf.columns:
    #     return rundf
    rttol = settings.rtTolerance
    rt = rundf["retention_time_sec"].apply(
        lambda rt: pd.Series(dict(rtmin=rt - rttol, rtmax=rt + rttol)),
    )
    return rundf.join(rt)


def findrt(
    rundf: pd.DataFrame,
    rt: pd.Series,
    settings: PeptideSettings,
) -> pd.DataFrame:
    use_in_sample = settings.retentionTimeCorrection == "UseInSample"
    rttol = settings.rtTolerance

    def rtrange(row: pd.Series) -> pd.Series:
        rts = row.retention_time_sec  # from pep.xml file
        if use_in_sample and row.isLabelledRun:
            rtmin = rts - rttol / 2
            rtmax = rts + rttol / 2

        else:
            rtmin = rts - rttol
            rtmax = rts + rttol

        rt_count = ((rt >= rtmin) & (rt <= rtmax)).sum()

        return pd.Series(
            dict(rtmin=rtmin, rtmax=rtmax, rt_count=float(rt_count)),
            dtype=np.float32,
        )

    return rundf[["retention_time_sec", "isLabelledRun"]].apply(rtrange, axis=1)


def findrt_dino(  # pragma: no cover
    dino_df: pd.DataFrame,
    rundf: pd.DataFrame,
    rt: pd.Series,
    settings: PeptideSettings,
) -> pd.DataFrame:
    use_in_sample = settings.retentionTimeCorrection == "UseInSample"

    dinomz = dino_df["mz"]
    rttol = settings.rtTolerance

    def findrtrange(row: pd.Series) -> pd.Series:
        total = 0
        rtmin = 1e10
        rtmax = -1.0
        rt_count = 0
        for mzin, mzmax in row.mzranges:
            q = (dinomz >= mzin) & (dinomz <= mzmax)
            n = q.sum()
            if n > 0:
                df = dino_df[q]
                rtmin = min(rtmin, df.rtStart.min())
                rtmax = max(rtmax, df.rtEnd.max())
            total += n
            if not total:
                if use_in_sample and row.isLabelledRun:
                    rtmin = row.retention_time_sec - rttol / 2
                    rtmax = row.retention_time_sec + rttol / 2
                else:
                    rtmin = row.retention_time_sec - rttol
                    rtmax = row.retention_time_sec + rttol
            rt_count = ((rt >= rtmin) & (rt <= rtmax)).sum()
        return pd.Series(
            dict(rtmin=rtmin, rtmax=rtmax, rt_count=float(rt_count)),
            dtype=np.float32,
        )

    return rundf[["mzranges", "retention_time_sec", "isLabelledRun"]].apply(
        findrtrange,
        axis=1,
    )


def mzml_calc_mzml_envelopes(
    rundf: pd.DataFrame,
    mzmlc: MZI,
    settings: PeptideSettings,
    level: int = 0,
    number_of_bg_processes: int = 1,
) -> list[dict[str, Any]]:
    from .logger import log_iterator
    from .config import MIN_RT

    n = len(rundf)
    rundf = calc_rtranges(
        rundf,
        mzmlc,
        settings,
        rt_min=MIN_RT,
    )
    logger.info(
        "%s[%d/%d]: removed out of range rt,mz %d/%d",
        mzmlc.name,
        level,
        number_of_bg_processes,
        len(rundf),
        n,
    )
    total = len(rundf)
    it = log_iterator(
        rundf.itertuples(index=True),
        total=total,
        desc=mzmlc.name,
        level=level,
        number_of_bg_processes=number_of_bg_processes,
    )
    row: PepXMLRunRowRT
    done = []
    # nhits = 0
    for row in it:  # type: ignore
        idx = row[0]
        d, fail = mzml_calc_pep_envelopes(mzmlc, row, settings)
        if d is None:
            continue
        d["peptide_index"] = idx
        d["peptide"] = row.peptide  # don't need this just sanity check
        d["fail"] = fail
        # d['runName'] = mzmlc.mzmlfile.runName

        done.append(d)
    logger.info(
        "%s[%d/%d]: found %d/%d envelopes",
        mzmlc.name,
        level,
        number_of_bg_processes,
        len(done),
        total,
    )
    return done


def mzml_calc_pep_envelopes(
    mzmlc: MZI,
    row: PepXMLRunRowRT,
    settings: PeptideSettings,
) -> tuple[dict[str, Any] | None, int]:
    from .config import MIN_RT

    rtmin, rtmax = row.rtmin, row.rtmax
    debug = logger.isEnabledFor(logging.DEBUG)

    start = datetime.now()
    eic = mzmlc.getEIC(row.mzranges, rtmin, rtmax, minrt=MIN_RT)
    if eic is None:  # pragma: no cover
        return None, 1 << FAIL_E_NOEICS
    end = datetime.now()

    if debug:  # pragma: no cover
        logger.debug("getEIC: %s %s %d", row.peptide, end - start, len(eic))

    maxIso = row.maxIso
    assert len(eic) == maxIso + 2

    start = end
    e, fail = fitEnvelope(row.peptide, eic, settings)
    if e is None:
        return None, fail
    if debug:  # pragma: no cover
        logger.debug("fitEnvelope: %s %s", row.peptide, datetime.now() - start)
    d = dict(eics=eic)
    d.update(asdict(e))
    return d, fail


def turnover_prepare(
    files: ResourceFiles,
    force: bool = False,
    workers: int = 1,
) -> None:
    """prepare pepXML and mzmlFiles"""
    from functools import partial
    from .pepxml import pepxml_create
    from .protxml import protxml_create
    from .parallel_utils import parallel_result

    if len(files.mzmlfiles) == 0:  # pragma: no cover
        logger.warning("no mzML files!")
        return

    files.ensure_directories()

    procs: list[
        tuple[
            Callable[[Any, int, int], int],
            MzMLResourceFile | PepXMLResourceFile | ProtXMLResourceFile,
        ]
    ] = []

    for pepxml in files.pepxmls:
        if force or not pepxml.cache_pepxml_ok():
            procs.append((pepxml_create, pepxml))

        else:
            logger.info(
                'skipping creation of "%s" cache: %s',
                pepxml.name,
                pepxml.cache_pepxml().name,
            )
    if files.protxml.exists():
        if force or not files.protxml.cache_protxml_ok():
            procs.append((protxml_create, files.protxml))

        else:
            logger.info(
                'skipping creation of "%s" cache: %s',
                files.protxml.name,
                files.protxml.cache_protxml().name,
            )
    todo = (
        [t for t in files.mzmlfiles if not t.cache_mzml_ok()]
        if not force
        else files.mzmlfiles
    )
    skipped = set(files.mzmlfiles) - set(todo)
    if skipped:  # pragma: no cover
        for t in skipped:
            logger.info(
                'skipping creation of "%s" cache: %s',
                t.name,
                t.cache_mzml().name,
            )
    target: MzMLResourceFile | PepXMLResourceFile | ProtXMLResourceFile
    for target in todo:
        procs.append((mzml_create, target))

    if not procs:  # pragma: no cover
        return
    cleanups: dict[int, BaseResourceFile] = {}
    exe: list[Callable[[], int]] = []
    for idx, (func, target) in enumerate(procs, start=1):
        exe.append(partial(func, target, idx, len(procs)))
        cleanups[idx] = target

    ntotal = len(exe)
    try:
        for ridx in parallel_result(exe, workers=workers):
            logger.info("turnover_prepare task done: [%d/%d]", ridx, ntotal)
            if ridx in cleanups:
                del cleanups[ridx]

    except KeyboardInterrupt:  # pragma: no cover
        for c in cleanups.values():
            c.cleanup()
        raise
