from __future__ import annotations

import re
import sys
import tomllib
import unicodedata
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import fields
from dataclasses import MISSING
from dataclasses import replace
from os.path import commonprefix
from os.path import sep
from pathlib import Path
from typing import Any
from typing import Sequence

import tomli_w

from .resourcefiles import MzMLResourceFile
from .resourcefiles import PepXMLResourceFile
from .resourcefiles import ProtXMLResourceFile
from .resourcefiles import ResourceFiles
from .utils import PeptideSettings

try:
    from unidecode import unidecode  # type: ignore
except ImportError:  # pragma: no cover

    def unidecode(string: str, errors: str = "ignore", replace_str: str = "?") -> str:
        return unicodedata.normalize("NFKD", string)


WIDE = sys.maxunicode > 0xFFFF  # UCS-4 build of python


def find_prefix(filenames: Sequence[Path]) -> Path:
    prefix = commonprefix([Path(m).absolute() for m in filenames])
    if not prefix.endswith(sep):
        i = prefix.rfind(sep)
        if i > 0:
            prefix = prefix[: i + 1]
    return Path(prefix)


def jobidkey(
    pepxml: str,
    protxml: str,
    mzmlfiles: list[str],
) -> str:  # pragma: no cover
    from hashlib import md5

    m = md5()
    m.update(str(Path(pepxml).resolve()).encode("utf-8"))
    m.update(str(Path(protxml).resolve()).encode("utf-8"))
    for s in mzmlfiles:
        m.update(str(Path(s).resolve()).encode("utf-8"))

    return m.hexdigest()


## @export
def slugify(s: str, transliterate: bool = True) -> str:
    if not s:
        return s

    if WIDE and transliterate:  # UCS-4 build of python
        s = unidecode(s)
    else:  # pragma: no cover
        s = unicodedata.normalize("NFKD", s)

    slug = s.encode("ascii", "ignore").lower()
    slug = re.sub(b"[^a-z0-9]+", b"-", slug).strip(b"-")
    slug = re.sub(b"[-]+", b"-", slug)
    return slug.decode("ascii")


## @export
@dataclass(kw_only=True)
class TurnoverJob:
    job_name: str
    pepxml: list[str]
    mzmlfiles: list[str]
    protxml: str = ""
    jobid: str = ""
    settings: PeptideSettings = PeptideSettings()
    cache_dir: str | None = None
    email: str | None = None
    status: str | None = None  # pending, started, finished, failed, stopped.
    mzfile_to_run: dict[str, str] | None = None
    match_runNames: bool = False
    aggregate_peptides: bool = True
    """Aggregate peptides and group by peptide, modification, assumed_charge and calc_neutral_pep_mass"""
    auto_generated_jobid: bool = False
    """Match peptides to mzML files via their `spectrum` names"""

    def __post_init__(self) -> None:
        if self.jobid == "":
            self.jobid = slugify(self.job_name)[:24]

    def cache_ok(self) -> bool:  # pragma: no cover
        return len(self.to_resource_files().todo()) == 0

    def get_mzfile_to_run(self) -> dict[str, str]:
        if self.mzfile_to_run is None:
            self.mzfile_to_run = {}
        for mz in self.mzmlfiles:
            pmz = Path(mz)
            if pmz.name not in self.mzfile_to_run:
                self.mzfile_to_run[pmz.name] = pmz.stem
        return self.mzfile_to_run

    @property
    def runNames(self) -> set[str]:
        return set(self.get_mzfile_to_run().values())

    def hash(self) -> str:
        from hashlib import md5

        m = md5()
        m.update(self.settings.hash().encode("utf-8"))
        for pepxml in self.pepxml:
            m.update(str(Path(pepxml).resolve()).encode("utf-8"))
        m.update(str(Path(self.protxml).resolve()).encode("utf-8"))
        for mzml in self.mzmlfiles:
            m.update(str(Path(mzml).resolve()).encode("utf-8"))
        for field in fields(self):
            if field.name in {
                "settings",
                "pepxml",
                "protxml",
                "mzmlfiles",
                "mzfile_to_run",
            }:
                continue
            v = getattr(self, field.name)
            m.update(str(v).encode("utf-8"))
        return m.hexdigest()

    def __hash__(self) -> int:
        return int(self.hash(), 16)

    def save_to_dir(
        self,
        directory: Path | str | None = None,
        filename: str | None = None,
    ) -> Path:
        outdir = Path(directory or self.cache_dir or ".")

        if filename is None:  # pragma: no cover
            out = outdir.joinpath(self.jobid + ".toml")
        else:
            if not filename.endswith(".toml"):
                filename += ".toml"
            out = outdir.joinpath(filename)

        if not out.parent.is_dir():  # pragma: no cover
            out.parent.mkdir(parents=True)

        return self.save_file(out)

    def save_file(self, out: Path) -> Path:
        mzmlfiles = [Path(m).resolve() for m in self.mzmlfiles]
        prefix = find_prefix(mzmlfiles)

        d = {k: v for k, v in asdict(self).items() if v is not None}

        if "cache_dir" in d:
            d["cache_dir"] = str(Path(d["cache_dir"]).expanduser().absolute())

        d["pepxml"] = [str(Path(m).absolute()) for m in self.pepxml]
        d["protxml"] = str(Path(d["protxml"]).absolute())
        d["mzmlfiles"] = [str(f.relative_to(prefix)) for f in mzmlfiles]
        d["mzmlprefix"] = str(Path(prefix).absolute())
        # d["settings"] = asdict(d["settings"])
        # settings = d.pop("settings")
        # d.update(settings)
        if "auto_generated_jobid" in d:
            del d["auto_generated_jobid"]
        try:
            b = tomli_w.dumps(d).encode("utf-8")
            out.write_bytes(b)
        except Exception as e:  # pragma: no cover
            try:
                out.unlink(missing_ok=True)
            except OSError:
                pass
            raise e
        return out

    @classmethod
    def safe_jobid(
        cls,
        turnover_dict: dict[str, Any],
        filename: Path,
    ) -> str:  # pragma: no cover
        return filename.stem
        # job_name = str(turnover_dict["job_name"])
        # return safe_jobid(job_name, filename)

    @classmethod
    def restore(cls, filename: str | Path) -> TurnoverJob:
        def ensure_list(key: str) -> None:
            if key in turnover_dict:
                r = turnover_dict[key]
                if isinstance(r, str):
                    turnover_dict[key] = [r]

        filename = Path(filename).expanduser()
        with filename.open("rb") as fp:
            turnover_dict: dict[str, Any] = tomllib.load(fp)
            # just what we want...

            ensure_list("mzmlfiles")
            ensure_list("pepxml")
            if "job_name" not in turnover_dict:
                raise ValueError("please specify a job_name")
            if "jobid" not in turnover_dict:
                turnover_dict["jobid"] = cls.safe_jobid(turnover_dict, filename)
                turnover_dict["auto_generated_jobid"] = True
            if "mzmlprefix" in turnover_dict:
                prefix = Path(turnover_dict.pop("mzmlprefix"))
                turnover_dict["mzmlfiles"] = [
                    str(prefix.joinpath(m)) for m in turnover_dict["mzmlfiles"]
                ]
            if "settings" in turnover_dict:
                settings = turnover_dict["settings"]
                settingsd = {
                    f.name: settings[f.name]
                    for f in fields(PeptideSettings)
                    if f.name in settings
                }
                turnover_dict["settings"] = PeptideSettings(**settingsd)
            else:
                settingsd = {
                    f.name: turnover_dict[f.name]
                    for f in fields(PeptideSettings)
                    if f.name in turnover_dict
                }
                turnover_dict["settings"] = PeptideSettings(**settingsd)
            if "protxml" not in turnover_dict:
                turnover_dict["protxml"] = ""

            missing = {k for k in REQUIRED_FIELDS if k not in turnover_dict}
            if missing:
                s = "" if len(missing) > 1 else ""
                raise ValueError(
                    f'turnover file "{filename}" is missing: {", ".join(missing)} value{s}',
                )
            # cleanup
            turnover_dict = {k: v for k, v in turnover_dict.items() if k in ALL_FIELDS}
            return cls(**turnover_dict)

    def relative_to_path(self, path: Path | str) -> TurnoverJob:
        rep: dict[str, Any] = {}
        path = Path(path)

        def topath(p: str) -> str:
            return str(path.joinpath(Path(p)))

        if self.protxml != "":
            rep["protxml"] = topath(self.protxml)
        rep["pepxml"] = [topath(p) for p in self.pepxml]
        rep["mzmlfiles"] = [topath(p) for p in self.mzmlfiles]
        if self.cache_dir is not None:
            rep["cache_dir"] = topath(self.cache_dir)
        return replace(self, **rep)

    def verify(self) -> str | None:
        return verify_run(self)

    def to_resource_files(self) -> ResourceFiles:
        rf = ResourceFiles(
            [PepXMLResourceFile(m, self.cache_dir) for m in set(self.pepxml)],
            ProtXMLResourceFile(self.protxml, self.cache_dir),
            [MzMLResourceFile(m, self.cache_dir) for m in set(self.mzmlfiles)],
        )
        return rf


ALL_FIELDS = {f.name for f in fields(TurnoverJob)}
REQUIRED_FIELDS = {f.name for f in fields(TurnoverJob) if f.default == MISSING}


def verify_run(
    job: TurnoverJob,
) -> str | None:
    # import pandas as pd
    # from .types.checking import check_pepxml_columns
    # from .utils import IO

    files = job.to_resource_files()
    msgs = []
    if not files.protxml.exists():
        msgs.append(f"no prot XML file: {files.protxml.original}")
    elif not files.protxml.cache_protxml_ok():
        msgs.append(f"cache for {files.protxml.original} is out of date or missing")

    # df = None
    for pepxml in files.pepxmls:
        if not pepxml.exists():
            msgs.append(f"no pep XML file: {pepxml.original}")
        elif not pepxml.cache_pepxml_ok():
            msg = f"cache for {pepxml.original.name} is out of date or missing"
            msgs.append(msg)
        # else:
        #     fname = pepxml.cache_pepxml()
        #     ndf = IO(fname).read_df()
        #     missing = check_pepxml_columns(ndf)
        #     if missing:
        #         msgs.append(f"columns missing {fname}: {missing}")

        #     if df is not None:
        #         df = pd.concat([df, ndf], axis=0)
        #     else:
        #         df = ndf

    # ok = True
    failed = [mzml for mzml in files.mzmlfiles if not mzml.exists()]
    if failed:
        for mzml in failed:
            msg = f"no mzML {mzml.original.name} file"
            msgs.append(msg)

        # ok = False

    failed = [
        mzml for mzml in files.mzmlfiles if mzml.exists() and not mzml.cache_mzml_ok()
    ]
    if failed:
        for mzml in failed:
            msg = f"cache for {mzml.original.name} is out of date or missing"
            msgs.append(msg)
        # ok = False

    # if ok and df is not None:
    #     if job.match_runNames:
    #         mzfile_to_run = job.get_mzfile_to_run()
    #         for mzml in files.mzmlfiles:
    #             hits = (df["run"] == mzfile_to_run[mzml.name]).sum()
    #             if hits == 0:
    #                 msg = f"no run hits in {mzml.original.name} for {mzml.name}"
    #                 msgs.append(msg)

    if not msgs:  # pragma: no cover
        return None
    return ", ".join(msgs)


def same_files(job1: TurnoverJob, job2: TurnoverJob) -> str | None:
    def issame(l1: list[str], l2: list[str]):
        p1 = [Path(p).resolve() for p in l1]
        p2 = [Path(p).resolve() for p in l2]
        if len(p1) != len(p2):
            return "different lengths"
        if not all(f1 == f2 for f1, f2 in zip(p1, p2)):
            return "files differ"
        return None

    msgs = []
    r = issame(job1.pepxml, job2.pepxml)
    if r is not None:
        msgs.append(f"pepxml: {r}")

    r = issame(job1.mzmlfiles, job2.mzmlfiles)
    if r is not None:
        msgs.append(f"mzml: {r}")

    if job1.protxml != "" or job2.protxml != "":
        r = issame([job1.protxml], [job2.protxml])
        if r is not None:
            msgs.append(f"protxml: {r}")
    if not msgs:
        return None
    return ", ".join(msgs)
