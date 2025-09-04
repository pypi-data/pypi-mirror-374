from __future__ import annotations

import math
from contextlib import suppress
from dataclasses import asdict
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Any
from typing import Literal
from typing import TYPE_CHECKING
from typing import TypedDict

import numpy as np
import pandas as pd
from typing_extensions import ReadOnly
# from typing import overload


if TYPE_CHECKING:
    from .types.pepxmltypes import PepXMLRunRow


## @export
@dataclass(kw_only=True)
class PeptideSettings:
    rtTolerance: float = 15.0  # seconds
    mzTolerance: float = 1e-5
    labelledIsotopeNumber: int = 15
    labelledElement: str = "N"
    maximumLabelEnrichment: float = 0.95
    retentionTimeCorrection: Literal["UseInSample", "SimpleMedian"] = "SimpleMedian"
    useObservedMz: bool = False
    minProbabilityCutoff: float = 0.8
    enrichmentColumns: int = 10

    def __post_init__(self) -> None:
        err = self.validate()
        if err is not None:
            raise ValueError(err)

    def validate(self) -> str | None:
        msgs = []
        ok = True
        if self.labelledElement not in ATOMICPROPERTIES:
            msgs.append(f"unknown element {self.labelledElement}")
            ok = False
        elif (
            self.labelledIsotopeNumber
            not in ATOMICPROPERTIES[self.labelledElement]["isotopeNr"]
        ):
            ok = False
            msgs.append(
                f"unknown isotopeNumber {self.labelledIsotopeNumber} for {self.labelledElement}",
            )
        if getNr(self.labelledElement) == self.labelledIsotopeNumber:
            msgs.append(
                f"labelledIsotopeNumber {self.labelledIsotopeNumber} for {self.labelledElement} cannot be the stable isotope!",
            )
        if self.mzTolerance <= 0:
            msgs.append("mzTolerance must be postive!")

        if self.rtTolerance <= 0:
            msgs.append("rtTolerance must be postive!")
        if self.retentionTimeCorrection not in ["UseInSample", "SimpleMedian"]:
            msgs.append(
                'retentionTimeCorrection should be "UseInSample" or "SimpleMedian"',
            )

        # enrichment columns <=0 means use elementCount for number of columns
        # see PeptideInfo.getEnrichments
        # if self.enrichmentColumns <= 0: #
        #     msgs.append("enrichmentColumns must be postive!")

        if self.maximumLabelEnrichment <= 0 or self.maximumLabelEnrichment > 1.0:
            msgs.append(
                f"maximumLabelEnrichment {self.maximumLabelEnrichment} must be between zero and 1!",
            )

        if self.minProbabilityCutoff <= 0 or self.minProbabilityCutoff > 1.0:
            msgs.append(
                f"minProbabilityCutoff {self.minProbabilityCutoff} must be between zero and 1!",
            )

        if ok:  # so self.abundance works
            if self.abundance >= self.maximumLabelEnrichment:
                msgs.append(
                    f'maximumLabelEnrichment "{self.maximumLabelEnrichment}"'
                    f' cannot be less than the environmental isotopic abundance "{self.abundance}"',
                )
        if not msgs:
            return None
        return ", ".join(msgs)

    def hash(self) -> str:
        from hashlib import md5

        m = md5()
        for k, v in asdict(self).items():
            if isinstance(v, float):
                v = signif(v, 6)
            m.update(f"{k}={v}".encode())
        return m.hexdigest()

    def __hash__(self) -> int:
        return int(self.hash(), 16)

    @property
    def labelledAtomicAbundancesAtMaxEnrich(self) -> np.ndarray:
        return labelledAtomicAbundancesAtMaxEnrich(self)

    @property
    def iabundance(self) -> int:
        return getIabundance(self)

    @property
    def abundance(self) -> float:
        return getAbundance(self)

    @property
    def naturalAtomicAbundances(self) -> np.ndarray:
        return naturalAtomicAbundances(self.labelledElement)

    def labelledAtomicAbundances(self, abundance: float) -> np.ndarray:
        return labelledAtomicAbundances(
            self.labelledIsotopeNumber,
            self.labelledElement,
            abundance,
        )

    # def getEnrichments(self, peptide: str) -> np.ndarray:
    #     return getEnrichments(peptide, self)

    def getEnrichmentsN(self, ncols: int) -> np.ndarray:
        return getEnrichmentsN(ncols, self)

    def isoMzDiff(self, assumed_charge: int) -> float:
        return isoMzDiff(assumed_charge, self)

    def getElementCount(self, formula: np.ndarray) -> int:
        return getElementCount(formula, self.labelledElement)

    def getElementCountFromPeptide(self, peptide: str) -> int:
        return self.getElementCount(peptideFormula(peptide))

    def eic_mzranges(self, pep: PepXMLRunRow) -> np.ndarray:
        return eic_mzranges(pep, self)


class PeptideInfo:
    def __init__(self, peptide: str, settings: PeptideSettings) -> None:
        self.peptide = peptide
        self.settings = settings
        self._formula: np.ndarray | None = None

    @property
    def formula(self) -> np.ndarray:
        if self._formula is None:
            self._formula = peptideFormula(self.peptide)
        return self._formula

    @property
    def elementCount(self) -> int:
        return self.settings.getElementCount(self.formula)

    def getEnrichments(self, maxIso: int | None = None) -> np.ndarray:
        """enrichmentColumns array of enrichments"""
        ncols = self.settings.enrichmentColumns
        if ncols <= 0:
            ncols = self.elementCount
        elif ncols == 1:
            if maxIso is None:
                raise ValueError("getEnrichments: can't determine maxIso!")
            ncols = maxIso + 1  # make it square....
        return self.settings.getEnrichmentsN(ncols)

    @property
    def naturalAtomicAbundances(self) -> np.ndarray:
        return self.settings.naturalAtomicAbundances

    def labelledAtomicAbundances(self, abundance: float) -> np.ndarray:
        return self.settings.labelledAtomicAbundances(abundance)

    @property
    def iabundance(self) -> int:
        return self.settings.iabundance

    @property
    def abundance(self) -> float:
        return self.settings.abundance


NPA = np.array


def NPI(list_of_ints: list[int]) -> np.ndarray[Any, np.dtype[np.int32]]:
    return np.array(list_of_ints, dtype=np.int32)


NAMES = np.array(["C", "H", "O", "N", "P", "S", "Se"])
NAMES_DICT = {n: i for i, n in enumerate(NAMES)}
WATER = NPI([0, 2, 1, 0, 0, 0, 0])
# "C", "H", "O" ,"N", "P", "S" , "Se"
# minus H20
AMINOACIDS = {
    "A": NPI([3, 5, 1, 1, 0, 0, 0]),  # Alanine, ala
    "C": NPI([3, 5, 1, 1, 0, 1, 0]),  # Cysteine, cys
    "D": NPI([4, 5, 3, 1, 0, 0, 0]),  # Aspartic Acid, asx
    "E": NPI([5, 7, 3, 1, 0, 0, 0]),  # Glutamic acid, glu
    "F": NPI([9, 9, 1, 1, 0, 0, 0]),  # Phenylalanine, phe
    "G": NPI([2, 3, 1, 1, 0, 0, 0]),  # Glycine, gly
    "H": NPI([6, 7, 1, 3, 0, 0, 0]),  # Histidine, his
    "I": NPI([6, 11, 1, 1, 0, 0, 0]),  # Isoleucine, ile
    "K": NPI([6, 12, 1, 2, 0, 0, 0]),  # Lysine, lys
    "L": NPI([6, 11, 1, 1, 0, 0, 0]),  # Leucine, leu
    "M": NPI([5, 9, 1, 1, 0, 1, 0]),  # Methionine, met
    "N": NPI([4, 6, 2, 2, 0, 0, 0]),  # Asparagine, asn
    "P": NPI([5, 7, 1, 1, 0, 0, 0]),  # Proline, pro
    "Q": NPI([5, 8, 2, 2, 0, 0, 0]),  # Glutamine, gln
    "R": NPI([6, 12, 1, 4, 0, 0, 0]),  # Arginine, arg
    "S": NPI([3, 5, 2, 1, 0, 0, 0]),  # Serine, ser
    "T": NPI([4, 7, 2, 1, 0, 0, 0]),  # Threonine, thr
    "V": NPI([5, 9, 1, 1, 0, 0, 0]),  # Valine, val
    "W": NPI([11, 10, 1, 2, 0, 0, 0]),  # Tryptophan, trp
    "Y": NPI([9, 9, 2, 1, 0, 0, 0]),  # Tyrosine, tyr
    "a": NPI([2, 2, 1, 0, 0, 0, 0]),
    "c": NPI([5, 8, 2, 2, 0, 1, 0]),
    "m": NPI([5, 9, 2, 1, 0, 1, 0]),
    "U": NPI([3, 5, 1, 1, 0, 0, 1]),
}


class AtomicProperties(TypedDict):
    isotopeNr: ReadOnly[np.ndarray[Any, np.dtype[np.int32]]]
    abundance: ReadOnly[np.ndarray[Any, np.dtype[np.float64]]]
    mass: ReadOnly[np.ndarray[Any, np.dtype[np.float64]]]


# WARNING! the zeroth value is assumed to be the "natural" isotope.
ATOMICPROPERTIES: dict[str, AtomicProperties] = dict(
    C=AtomicProperties(
        isotopeNr=NPI([12, 13]),
        mass=NPA([12.0, 13.0033548378]),
        abundance=NPA([0.9889, 0.0111]),
    ),
    H=AtomicProperties(
        isotopeNr=NPI([1, 2]),
        mass=NPA([1.0078250321, 2.0141017780]),
        abundance=NPA([0.9998, 0.0001]),
    ),
    O=AtomicProperties(
        isotopeNr=NPI([16, 17, 18]),
        mass=NPA([15.9949146, 16.9991312, 17.9991603]),
        abundance=NPA([0.9976, 0.0004, 0.0020]),
    ),
    N=AtomicProperties(
        isotopeNr=NPI([14, 15]),
        mass=NPA([14.0030740052, 15.0001088984]),
        abundance=NPA([0.99633, 0.00367]),
    ),
    # need entry for formula calculation...
    P=AtomicProperties(
        isotopeNr=NPI([31]),
        mass=NPA([30.97376163]),
        abundance=NPA([1.0]),
    ),
    S=AtomicProperties(
        isotopeNr=NPI([32, 33, 34, 36]),
        mass=NPA([31.97207070, 32.97145843, 33.96786665, 35.96708062]),
        abundance=NPA([0.9502, 0.0075, 0.0421, 0.0002]),
    ),
    # out of (isotope number) order abundance...
    Se=AtomicProperties(
        isotopeNr=NPI([80, 78, 76, 82, 77, 74]),
        mass=NPA(
            [79.9165213, 77.9173091, 75.9192136, 81.9166994, 76.919914, 73.9224764],
        ),
        abundance=NPA([0.4961, 0.2377, 0.0937, 0.0873, 0.0763, 0.0089]),
    ),
)


## @export
def get_isotope_numbers() -> dict[str, list[int]]:
    return {
        elem: [int(n) for n in d["isotopeNr"]] for elem, d in ATOMICPROPERTIES.items()
    }


## @export
def get_element_names() -> list[str]:
    return list(NAMES)


def getNr(element: str) -> int:
    """get isotope number for most abundant element"""
    if element not in ATOMICPROPERTIES:
        raise ValueError(f'unknown element: "{element}"')
    at = ATOMICPROPERTIES[element]
    a = at["abundance"]
    return int(at["isotopeNr"][a.argmax()])


def getDefaultIsotopeNr(element: str) -> int:
    """get default isotope number for experiment"""
    if element not in ATOMICPROPERTIES:
        raise ValueError(f'unknown element: "{element}"')
    at = ATOMICPROPERTIES[element]
    a = at["isotopeNr"]
    return int(a[1])


def getElementCount(formula: np.ndarray, element: str) -> int:
    return formula[NAMES == element][0]


def okNr(element: str) -> set[int]:
    """set of possible atomic numbers"""
    at = ATOMICPROPERTIES[element]
    a = at["isotopeNr"]
    return {int(i) for i in a}


# return C H O N P S Se count list
def peptideFormula(peptideSequence: str) -> np.ndarray[Any, np.dtype[np.int32]]:
    return reduce(
        lambda total, aa: total + AMINOACIDS[aa],
        list(peptideSequence),
        WATER,
    )


def getIabundance(settings: PeptideSettings) -> int:
    a = ATOMICPROPERTIES[settings.labelledElement]
    b = a["isotopeNr"] == settings.labelledIsotopeNumber
    return np.where(b)[0][0]


def getAbundance(setting: PeptideSettings) -> float:
    a = ATOMICPROPERTIES[setting.labelledElement]
    b = a["isotopeNr"] == setting.labelledIsotopeNumber
    return a["abundance"][b][0]


def getEnrichmentsN(
    elementCount: int,
    settings: PeptideSettings,
) -> np.ndarray[Any, np.dtype[np.floating[Any]]]:
    return np.linspace(
        settings.abundance,
        settings.maximumLabelEnrichment,
        elementCount,
        endpoint=True,
    )


def labelledAtomicAbundances(
    labelledIsotopeNumber: int,
    element: str,
    abundance: float,
) -> np.ndarray:
    if element in ATOMICPROPERTIES:
        if abundance < 0.0 or abundance > 1.0:
            raise ValueError(f'abundance "{abundance}" must be between 0 and 1')
        ap = ATOMICPROPERTIES[element]
        if labelledIsotopeNumber in ap["isotopeNr"]:
            a = ap["abundance"]
            label = ap["isotopeNr"] == labelledIsotopeNumber
            adjustedAbundance: np.ndarray = (1 - abundance) * a / np.sum(a[~label])

            adjustedAbundance[label] = abundance
            return adjustedAbundance
    raise ValueError(f"unknown element: {element}[{labelledIsotopeNumber}]")


def naturalAtomicAbundances(
    element: str,
) -> np.ndarray:
    if element in ATOMICPROPERTIES:
        ap = ATOMICPROPERTIES[element]
        return ap["abundance"]

    raise ValueError(f'unknown element: "{element}"')


def labelledAtomicAbundancesAtMaxEnrich(
    settings: PeptideSettings,
) -> np.ndarray:
    return labelledAtomicAbundances(
        settings.labelledIsotopeNumber,
        settings.labelledElement,
        settings.maximumLabelEnrichment,
    )


# def okiso(settings: PeptideSettings) -> bool:
#     props = ATOMICPROPERTIES[settings.labelledElement]
#     isotopeNr, abundance = props["isotopeNr"], props["abundance"]
#     idx = (isotopeNr == settings.labelledIsotopeNumber)[0]
#     ab = (abundance == np.max(abundance))[0]
#     return idx != ab


def isoMzDiff(assumed_charge: int, settings: PeptideSettings) -> float:
    props = ATOMICPROPERTIES[settings.labelledElement]
    mass, abundance = props["mass"], props["abundance"]
    pos = props["isotopeNr"] == settings.labelledIsotopeNumber
    isoDiff = mass[pos][0] - mass[abundance.argmax()]

    isoMzDiff = isoDiff / assumed_charge
    return isoMzDiff


@dataclass(kw_only=True)
class MZEICRecord:
    assumed_charge: int
    mz: float
    observed_mz: float
    maxIso: int

    @staticmethod
    def from_series(s: pd.Series):
        return MZEICRecord(**s.to_dict())


def eic_mzranges(
    pep: PepXMLRunRow | MZEICRecord,
    settings: PeptideSettings,
) -> np.ndarray:
    # requires
    # maxIso, mz, assumed_charge and
    # (settings.{labelledElement,labelledIsotopeNumber}, mzTolerance)
    isoDiff = settings.isoMzDiff(pep.assumed_charge)
    mz = pep.observed_mz if settings.useObservedMz else pep.mz
    tol = mz * settings.mzTolerance
    # NOTE: pep.maxIso might be a floating point number if
    # pep is actually a pd.Series
    isoRange = range(-1, round(pep.maxIso) + 1)
    mzranges = []
    for iso in isoRange:
        v = mz + iso * isoDiff
        mzranges.append([v - tol, v + tol])

    return np.array(mzranges, dtype=np.float32)


def resize(a: np.ndarray, width: int) -> np.ndarray:
    d = width - len(a)
    if d > 0:
        return np.pad(a, (0, d), "constant", constant_values=(0, 0))
    if d < 0:
        return a[:width]
    return a


def ensure_pos(a: np.ndarray) -> np.ndarray:
    # use np.fmax if we want to set a[i] to zero if a[i] is NaN
    return np.maximum(a, 0.0)
    # return np.where(a >= 0, a, 0.0)


# def roundit(n: float, nsig: int = 3) -> int:
#     from math import log10

#     assert n > 0, str(n)
#     pwr = round(log10(n))
#     pwr = max(0, pwr - nsig)
#     num = 10**pwr
#     return round(n / num) * num


def signif(x: float | int, digits: int = 6) -> float | int:
    if x == 0 or not math.isfinite(x):
        return x
    digits -= math.ceil(math.log10(abs(x)))
    return round(x, digits)


def human(num: int, suffix: str = "B", scale: int = 1) -> str:
    if not num:
        return f"0{suffix}"
    num *= scale
    magnitude = int(math.floor(math.log(abs(num), 1000)))
    val = num / math.pow(1000, magnitude)
    if magnitude > 7:
        return "{:.1f}{}{}".format(val, "Y", suffix)
    return "{:3.1f}{}{}".format(
        val,
        ["", "k", "M", "G", "T", "P", "E", "Z"][magnitude],
        suffix,
    )


def rmfiles(files: list[Path]) -> None:
    for f in files:
        with suppress(OSError):
            Path(f).unlink(missing_ok=True)


def duplicate_rows(df: pd.DataFrame, on: list[str]) -> pd.DataFrame:
    return df[df.duplicated(on, keep=False)]


def fdr(df: pd.DataFrame) -> float:  # pragma: no cover
    decoy = df["is_decoy"].sum()
    denom = len(df) - decoy
    return float(decoy) / denom if denom > 0 else np.inf


def calculate_fdrs(
    df: pd.DataFrame,
    nbins: int = 50,
    score: str = "peptideprophet_probability",
) -> pd.Series:
    """Requires peptideprophet_probability, is_decoy"""
    # df['fdr'] = calculate_fdrs(df)
    from math import ceil

    decoys = df["is_decoy"]
    pbins = df[score].apply(lambda p: ceil(p * nbins))

    mx = int(pbins.max())

    fdrs: dict[int, float] = {}
    for binno in range(mx + 1):
        target = pbins >= binno
        n = target.sum()
        if n == 0:  # pragma: no cover
            fdrs[binno] = fdrs.get(binno - 1, 0.0)
            continue
        ndecoys = decoys[target].sum()
        denom = n - ndecoys
        fdrs[binno] = ndecoys / denom if denom > 0 else np.inf
    return pbins.apply(lambda binno: fdrs[binno]).astype(np.float32)


class Apply:
    @staticmethod
    def eics_reshape(s: pd.Series) -> np.ndarray:  # pragma: no cover
        return s["eics"].reshape(s["eics_shape"])

    @staticmethod
    def eics_reshape_np(s: pd.Series) -> np.ndarray:
        return np.array(s["eics"]).reshape(s["eics_shape"])

    @staticmethod
    def modcol(mods: list[dict[str, int | float | str]], n: int = 3) -> str:
        mods = sorted(mods, key=lambda d: int(d["position"]))
        return ":".join([f"{float(d['mass']):.{n}f}@{d['position']}" for d in mods])

    @staticmethod
    def protxml_modcol(peptided: dict[str, Any], n: int = 3) -> pd.Series:
        name = peptided["peptide_sequence"]
        if "mod_aminoacid_mass" not in peptided:
            return pd.Series(dict(peptide=name, modcol=""))
        return pd.Series(
            dict(peptide=name, modcol=Apply.modcol(peptided["mod_aminoacid_mass"], n)),
        )

    # @staticmethod
    # def binrt(rt: float, rttol: float = 15.0) -> int: # pragma: no cover
    #     return round(rt / rttol)

    # @staticmethod
    # def binmz(mz: float, mztol: float = 10e-6) -> int:  # pragma: no cover
    #     return round(mz / mztol)


class IO:
    def __init__(self, filename: Path | str, df: pd.DataFrame | None = None):
        self.df = df
        self.filename = Path(filename)

    def save_df(self, index: bool = False) -> None:
        assert self.df is not None
        try:
            if not self.filename.parent.exists():  # pragma: no cover
                self.filename.parent.mkdir(parents=True, exist_ok=True)
            self.df.to_parquet(self.filename, index=index)

        except (Exception, KeyboardInterrupt):  # pragma: no cover
            rmfiles([self.filename])  # cleanup
            raise

    def read_df(self, columns: list[str] | None = None) -> pd.DataFrame:
        if self.filename.name.endswith(".feather"):  # pragma: no cover
            return pd.read_feather(self.filename, columns=columns, use_threads=True)
        return pd.read_parquet(self.filename, columns=columns, use_threads=True)


def df_can_write(fmt: Literal["excel", "parquet"]) -> bool:
    from io import BytesIO

    df = pd.DataFrame({"x": [0]})
    try:
        func = getattr(df, f"to_{fmt}", None)
        if func is None:  # pragma: no cover
            return False
        func(BytesIO())
        return True
    except ModuleNotFoundError:  # pragma: no cover
        return False


def df_can_write_parquet() -> bool:
    return df_can_write("parquet")


def df_can_write_excel() -> bool:
    return df_can_write("excel")


def getsize(fname: Path) -> int:
    return fname.stat().st_size


# @overload
# def array_split(df: pd.Series, num: int) -> list[pd.Series]: ...


# @overload
# def array_split(df: pd.DataFrame, num: int) -> list[pd.DataFrame]: ...


def array_split(
    df,
    num: int,
):
    w, e = divmod(len(df), num)
    if e > 0:
        w += 1
    ret = []
    for i in range(0, len(df), w):
        ret.append(df.iloc[i : i + w])
    return ret
