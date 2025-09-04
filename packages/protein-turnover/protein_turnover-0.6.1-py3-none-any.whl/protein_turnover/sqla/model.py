from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pandas as pd  # type: ignore
from sqlalchemy import Boolean
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import inspect
from sqlalchemy import Integer
from sqlalchemy import JSON
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.engine import Connectable
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .utils import check_missing_columns
from .utils import file2engine
from .utils import secondary

# func.count()
# pylint: disable=not-callable


class Base(DeclarativeBase):
    pass


class Modification(TypedDict):
    mass: float
    massdiff: float | None
    position: int
    site: str | None


class Peptide(Base):
    __tablename__ = "peptides"
    peptideid: Mapped[int] = mapped_column(Integer, primary_key=True)
    peptide: Mapped[str] = mapped_column(Text, nullable=False)
    assumed_charge: Mapped[int | None] = mapped_column(Integer)
    modcol: Mapped[str | None] = mapped_column(Text)
    calc_neutral_pep_mass: Mapped[float | None] = mapped_column(Float)
    precursor_neutral_mass: Mapped[float | None] = mapped_column(Float)
    peptideprophet_probability: Mapped[float | None] = mapped_column(Float)
    mz: Mapped[float | None] = mapped_column(Float)
    observed_mz: Mapped[float | None] = mapped_column(Float)
    retention_time_sec: Mapped[float | None] = mapped_column(Float)
    num_missed_cleavages: Mapped[int | None] = mapped_column(Integer)
    is_decoy: Mapped[bool | None] = mapped_column(Boolean)
    agg_count: Mapped[int | None] = mapped_column(Integer)
    protein_descr: Mapped[list[str] | None] = mapped_column(JSON)
    modifications: Mapped[list[Modification] | None] = mapped_column(JSON)
    run: Mapped[str | None] = mapped_column(String(64))
    isLabelledRun: Mapped[bool | None] = mapped_column(Boolean)
    fdr: Mapped[float | None] = mapped_column(Float)
    # ----- computed -----
    labelledElementCount: Mapped[int | None] = mapped_column(Integer)
    maxIso: Mapped[int | None] = mapped_column(Integer)
    mzranges: Mapped[list[float] | None] = mapped_column(JSON, deferred=True)
    eics: Mapped[list[float] | None] = mapped_column(JSON, deferred=True)
    adjustedRsq: Mapped[list[float] | None] = mapped_column(
        JSON,
        deferred=True,
    )  # list[float]
    isotopeEnvelopes: Mapped[list[float] | None] = mapped_column(JSON, deferred=True)
    monoPeakArea: Mapped[float | None] = mapped_column(Float)
    maxPeakArea: Mapped[float | None] = mapped_column(Float)
    monoFitParams: Mapped[list[float] | None] = mapped_column(JSON, deferred=True)
    inv_ratio: Mapped[float | None] = mapped_column(Float)
    labelledEnvelopes: Mapped[list[float] | None] = mapped_column(JSON, deferred=True)
    relativeIsotopeAbundance: Mapped[float | None] = mapped_column(Float)
    enrichment: Mapped[float | None] = mapped_column(Float)
    heavyCor: Mapped[float | None] = mapped_column(Float)
    heavyCor2: Mapped[float | None] = mapped_column(Float)
    theoreticalDist: Mapped[list[float] | None] = mapped_column(JSON, deferred=True)
    nnls_residual: Mapped[float | None] = mapped_column(Float)
    totalNNLSWeight: Mapped[float] = mapped_column(Float)
    totalIntensityWeight: Mapped[float] = mapped_column(Float)
    fail: Mapped[int] = mapped_column(Integer)
    eics_shape: Mapped[list[int] | None] = mapped_column(JSON, deferred=True)
    # list of protein names from ProtXML file (needed for website)
    protein_names: Mapped[list[str] | None] = mapped_column(JSON)

    iso_peaks_nr_20: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    iso_peaks_nr_40: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    iso_peaks_nr_60: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    iso_peaks_nr_80: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    proteins: Mapped[list[Protein]] = relationship(
        lambda: Protein,
        secondary="peptides_proteins",
        back_populates="peptides",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Peptide({self.peptide},{self.mz}, {self.assumed_charge})"


# if you change this then you must change
# the columns iso_peaks_nr_{N} above
## @export
MINRSQ100 = [20, 40, 60, 80]


class PI(TypedDict):
    protein_name: str


class PeptideData(TypedDict):
    calc_neutral_pep_mass: float
    charge: int
    exp_tot_instances: float
    fpkm_adjusted_probability: float
    group_weight: str  # str of float
    initial_probability: float
    is_contributing_evidence: bool
    is_nondegenerate_evidence: bool
    mod_aminoacid_mass: float | None
    mod_nterm_mass: float | None
    modified_peptide: str | None
    n_enzymatic_termini: int
    n_instances: int
    n_sibling_peptides: float
    n_sibling_peptides_bin: int
    nsp_adjusted_probability: float
    peptide_group_designator: str
    peptide_parent_protein: list[PI] | None
    peptide_sequence: str
    weight: float


class Protein(Base):
    __tablename__ = "proteins"

    proteinid: Mapped[int] = mapped_column(Integer, primary_key=True)
    probability: Mapped[int | None] = mapped_column(Float)
    group_number: Mapped[int | None] = mapped_column(Integer)
    protein_name: Mapped[str | None] = mapped_column(Text)
    n_indistinguishable_proteins: Mapped[int | None] = mapped_column(Integer)
    percent_coverage: Mapped[float | None] = mapped_column(Float)
    unique_stripped_peptides: Mapped[list[str] | None] = mapped_column(JSON)
    group_sibling_id: Mapped[str | None] = mapped_column(String(16))
    total_number_peptides: Mapped[int | None] = mapped_column(Integer)
    total_number_distinct_peptides: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float | None] = mapped_column(Float)
    peptide: Mapped[list[PeptideData] | None] = mapped_column(JSON)
    protein_description: Mapped[str | None] = mapped_column(Text)
    pct_spectrum_ids: Mapped[float | None] = mapped_column(Float)
    prot_length: Mapped[int | None] = mapped_column(Integer)
    indistinguishable_protein: Mapped[list[str] | None] = mapped_column(JSON)
    lpf_median: Mapped[float | None] = mapped_column(Float)
    lpf_std: Mapped[float | None] = mapped_column(Float)
    num_found_peptides: Mapped[int | None] = mapped_column(Integer)

    peptides: Mapped[list[Peptide]] = relationship(
        Peptide,
        secondary="peptides_proteins",
        back_populates="proteins",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"Protein({self.protein_name},prob={self.probability},npep={self.unique_stripped_peptides})"


class PepProt(Base):
    __tablename__ = "peptides_proteins"
    peptideid: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(Peptide.peptideid),
        nullable=False,
        primary_key=True,
    )
    proteinid: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(Protein.proteinid),
        nullable=False,
        primary_key=True,
    )


class Version(Base):
    __tablename__ = "version"
    version: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)


def aggregate_lpf(
    prot: pd.DataFrame,
    pep: pd.DataFrame,
    secondary: pd.DataFrame,
) -> pd.DataFrame:
    m = secondary.merge(pep, how="inner", left_on="peptideid", right_on="peptideid")
    a = (
        m.groupby("proteinid")
        .agg(
            lpf_median=pd.NamedAgg(column="relativeIsotopeAbundance", aggfunc="median"),
            lpf_std=pd.NamedAgg(column="relativeIsotopeAbundance", aggfunc="std"),
            num_found_peptides=pd.NamedAgg(column="peptideid", aggfunc="count"),
        )
        .reset_index()
    )
    a.fillna(0.0, inplace=True)

    return prot.merge(a, how="left", left_on="proteinid", right_on="proteinid")


def save_db(
    pep: pd.DataFrame,
    prot: pd.DataFrame,
    engine: Engine,
) -> tuple[int, int, int]:
    from .utils import dehydrate_peptides, dehydrate_prot
    from .iso_peaks import add_iso_peaks
    from ..config import SQLITE_VERSION

    pep = dehydrate_peptides(pep)
    prot = dehydrate_prot(prot)
    # pep["peptideid"] = pep.index + 1
    prot["proteinid"] = prot.index + 1
    sec, names = secondary(pep, prot)
    # add protein_names concatenation to peptide
    pep = pep.merge(names, how="left", left_on="peptideid", right_on="peptideid")
    # add iso_peaks_nrNN peaks
    pep = add_iso_peaks(pep)
    # don't save any proteins that don't exist
    prot = prot[prot["proteinid"].isin(sec["proteinid"])]
    prot = aggregate_lpf(prot, pep, sec)

    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        npep = save_df(pep, Peptide, conn)
        nprot = save_df(prot, Protein, conn)
        nsec = save_df(sec, PepProt, conn)
        version = pd.DataFrame({"version": [SQLITE_VERSION]})
        save_df(version, Version, conn)

    # populate_isoPeaksNrFixed(engine, force=True)
    return npep, nprot, nsec


def save_df(
    df: pd.DataFrame,
    Orm: type[Base],
    conn: Connectable,
    chunksize: int = 1000,
) -> int:
    i = inspect(Orm)
    dtypes = {c.name: c.type for c in i.columns}

    cols = [n for n in dtypes if n in df.columns]

    return df[cols].to_sql(
        i.local_table.name,  # type: ignore
        con=conn,
        # need this for some reason....
        dtype=dtypes,  # type: ignore
        chunksize=chunksize,
        if_exists="append",
        index=False,
    )


def check_missing_pep(pep: pd.DataFrame) -> set[str]:
    return check_missing_columns(pep, Peptide)


def check_missing_prot(prot: pd.DataFrame) -> set[str]:
    return check_missing_columns(prot, Protein)


def save_to_file(
    sqlfile: Path,
    pep: pd.DataFrame,
    prot: pd.DataFrame,
) -> tuple[int, int, int]:
    if sqlfile.exists():  # pragma: no cover
        sqlfile.unlink()

    engine = file2engine(sqlfile)
    try:
        return save_db(pep, prot, engine)
    finally:
        engine.dispose()
