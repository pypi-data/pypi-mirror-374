from __future__ import annotations

import operator
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import fields
from dataclasses import replace
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Literal
from typing import NamedTuple
from typing import NotRequired
from typing import TypedDict

import numpy as np
import pandas as pd  # type: ignore
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import join
from sqlalchemy import or_
from sqlalchemy import Select
from sqlalchemy import select
from sqlalchemy import Subquery
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm import Relationship
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.expression import BinaryExpression
from typing_extensions import override

from .model import PepProt
from .model import Peptide
from .model import Protein
from .utils import file2engine
from .utils import precision as to_precision
from .utils import rehydrate_peptides

# from sqlalchemy.orm import load_only
# from sqlalchemy.orm import selectinload
# from sqlalchemy.orm import Session


# func.count()
# pylint: disable=not-callable
class WhereClauses(NamedTuple):
    pep_where: ColumnElement[bool] | None
    prot_where: ColumnElement[bool] | None


INT_FORM_FIELDS = {"isoPeaksMinRSQ", "sqlite_version", "isoPeaksNr", "sqlite_version"}


## @export
@dataclass
class FormFilter:
    peptideQualityFilter: float | None = None
    heavyMinCor: float | None = None
    isoPeaksNr: int | None = None
    isoPeaksMinRSQ: int = -1
    #    heavyMinRSQ: float | None = None
    monoMinus1MinRatio: float | None = None
    # enrichmentFactor: float | None = None
    enrichmentMax: float | None = None
    enrichmentMin: float | None = None
    fdrMaximum: float | None = None
    nnlsResidual: float | None = None
    maxPeakArea: float | None = None
    log_sigma_lpf: float | None = None
    sqlite_version: int = -1

    def calc_where(self, scale_intensity: bool = False) -> WhereClauses:
        pep_filters = []
        prot_filters = []

        def add(q: Any) -> None:
            pep_filters.append(q)

        if self.peptideQualityFilter is not None:
            add(Peptide.peptideprophet_probability >= self.peptideQualityFilter)

        if self.fdrMaximum is not None:
            add(Peptide.fdr <= self.fdrMaximum)

        if self.heavyMinCor is not None:
            add(Peptide.heavyCor >= self.heavyMinCor)

        # if self.heavyMinRSQ is not None:
        #     add(Peptide.heavy_adj_r_squared >= self.heavyMinRSQ)

        if self.nnlsResidual is not None:
            if scale_intensity:  # pragma: no cover
                add(
                    Peptide.nnls_residual / Peptide.totalIntensityWeight
                    <= self.nnlsResidual,
                )
            else:
                add(
                    Peptide.nnls_residual / Peptide.totalNNLSWeight
                    <= self.nnlsResidual,
                )

            # add(func.power(Peptide.nnls_residual,2) <= self.nnlsResidual)
            # add(Peptide.nnls_residual <= self.nnlsResidual)

        if self.monoMinus1MinRatio is not None and self.monoMinus1MinRatio > 0.0:
            add(Peptide.inv_ratio < 1.0 / self.monoMinus1MinRatio)

        if self.enrichmentMax is not None:
            add(Peptide.enrichment <= self.enrichmentMax)
        if self.enrichmentMin is not None:
            add(Peptide.enrichment >= self.enrichmentMin)

        if self.maxPeakArea is not None:
            add(Peptide.maxPeakArea >= self.maxPeakArea)

        if self.log_sigma_lpf is not None:
            prot_filters.append(
                func.log((Protein.lpf_std + 1e-4) / Protein.lpf_median)
                <= self.log_sigma_lpf,
            )

        if (
            self.sqlite_version >= 1
            and self.isoPeaksNr is not None
            and self.isoPeaksMinRSQ is not None
            and self.isoPeaksMinRSQ != -1  # not set
        ):
            col = getattr(Peptide, f"iso_peaks_nr_{int(self.isoPeaksMinRSQ)}", None)
            if col is not None:
                add(col >= int(self.isoPeaksNr))

        return WhereClauses(
            and_(*pep_filters) if pep_filters else None,
            and_(*prot_filters) if prot_filters else None,
        )


FILTER_NAMES = {f.name for f in fields(FormFilter)}


def ident(s: str) -> str:
    return s


## @export
def dict_to_form_filter(
    d: dict[str, str],
    match: Callable[[str], str | None] = ident,
) -> FormFilter:
    ret: dict[str, float | int] = {}

    for k in d.keys():
        col = match(k)
        if col is not None:
            if col in FILTER_NAMES:
                value = d[k]
                if value:
                    ret[col] = int(value) if col in INT_FORM_FIELDS else float(value)
    return FormFilter(**ret)  # type: ignore


## @export
def all_plotting_columns() -> list[Column]:  # pragma: no cover
    from ..plotting import ALL_COLUMNS

    return [Column(c) for c in ALL_COLUMNS]


def like(attr: InstrumentedAttribute, value: str) -> BinaryExpression[bool]:
    if "%" not in value:
        value = "%" + value + "%"
    return attr.like(value)


def in_(attr: InstrumentedAttribute, value: str) -> BinaryExpression[bool]:
    return attr.in_(value)


def doregex(attr: InstrumentedAttribute, value: str) -> BinaryExpression[bool]:
    return attr.op("REGEXP")(value)  # need pcre installed in sqllite


OPMAP: dict[str, Callable[..., Any]] = {
    ">": operator.gt,
    ">=": operator.ge,
    "=": operator.eq,
    "<": operator.lt,
    "<=": operator.le,
    "!=": operator.ne,
    "like": like,
    "regex": doregex,
    "in": in_,
}


## @export
class RowQuery(NamedTuple):
    column: str
    op: str
    value: Any

    def to_sql(self, Orm: type[DeclarativeBase]) -> ColumnElement[bool]:
        attr = getattr(Orm, self.column, None)
        if attr is None or not hasattr(attr, "property"):
            raise ValueError(
                f"unknown column {self.column} for {Orm.__tablename__} table",
            )
        if isinstance(attr.property, Relationship):  # pragma: no cover
            raise ValueError(
                f"column {self.column} is a relationship on {Orm.__tablename__}!",
            )
        op = OPMAP.get(self.op)
        if op is None:
            raise ValueError(f"no operator like {self.op}")

        return op(attr, self.value)


## @export
@dataclass
class RowFilter:
    rows: list[RowQuery]
    method: Literal["and", "or"] = "and"

    # used in protein_turnover_website
    def add(self, more: RowFilter) -> RowFilter:
        return replace(self, rows=self.rows + more.rows)

    def to_and_sql(self, Orm: type[DeclarativeBase]) -> ColumnElement[bool]:
        return and_(*[q.to_sql(Orm) for q in self.rows])

    def to_or_sql(
        self,
        Orm: type[DeclarativeBase],
    ) -> ColumnElement[bool]:  # pragma: no cover
        return or_(*[q.to_sql(Orm) for q in self.rows])

    def to_sql(self, Orm: type[DeclarativeBase]) -> ColumnElement[bool]:
        if self.method == "and":
            return self.to_and_sql(Orm)
        return self.to_or_sql(Orm)  # pragma: no cover


## @export
@dataclass
class DTQuery:
    start: int = 0
    length: int = 10
    search: str | None = None
    regex: bool = False
    ascending: bool = True
    order_column: str | None = None
    draw: int = 0  # data tables


def search_protein_tosql(search: str, search_columns: list[str]) -> ColumnElement[bool]:
    return RowFilter(
        [RowQuery(coln, "like", search) for coln in search_columns],
    ).to_or_sql(Protein)


## @export
@dataclass
class ProteinQueryResult:
    result_df: pd.DataFrame
    total_proteins: int = -1
    total_peptides: int = -1
    total_filtered: int = -1


def np_agg(val: str | None, func: Callable[[np.ndarray], float]) -> float | None:
    if val is None:
        return None
    values = np.array([float(v) for v in val.split(",")])
    if len(values) == 0:  # pragma: no cover
        return np.nan
    return func(values)


def std(val: str | None) -> float | None:
    return np_agg(val, np.std)


def median(val: str | None) -> float | None:
    return np_agg(val, np.median)


# sqlite is missing some aggregate functions... we "fake" them here.
FAKE_AGGREGATE_FUNCS = {"std": std, "median": median}


class AGDict(TypedDict):
    column: str
    aggfunc: str
    label: NotRequired[str]
    args: NotRequired[Sequence[str] | str]
    denom: NotRequired[str]


# see https://www.sqlite.org/lang_aggfunc.html
## @export
@dataclass(kw_only=True)
class Aggregate:
    column: str
    aggfunc: str  # aggregate function sum,avg,group_concat etc.
    label: str = ""
    args: Sequence[str] | str = ()

    def __post_init__(self) -> None:
        if self.label == "":
            self.label = self.column
        if isinstance(self.args, str):  # pragma: no cover
            self.args = [self.args]

    def getattr(
        self,
        orm: type[DeclarativeBase],
        column: str,
    ) -> ColumnElement[Any]:
        attr = getattr(orm, column, None)
        if attr is None or not hasattr(attr, "property"):
            raise ValueError(f"unknown column {column} for {orm.__tablename__} table")
        if isinstance(attr.property, Relationship):  # pragma: no cover
            raise ValueError(
                f"column {column} is a relationship on {orm.__tablename__}!",
            )
        return attr

    def getcolumn(self, orm: type[DeclarativeBase]) -> ColumnElement[Any]:
        return self.getattr(orm, self.column)

    def make_column(self, orm: type[DeclarativeBase]) -> ColumnElement[Any]:
        attr = self.getcolumn(orm)

        if self.aggfunc in FAKE_AGGREGATE_FUNCS:
            aggf = getattr(func, "group_concat")
            attr = aggf(attr, ",")
        else:
            aggf = getattr(func, self.aggfunc)
            attr = aggf(attr, *self.args)
        return attr.label(self.label)


## @export
@dataclass(kw_only=True)
class RatioAggregate(Aggregate):
    denom: str = "totalNNLSWeight"

    @override
    def getcolumn(self, orm: type[DeclarativeBase]) -> ColumnElement[Any]:
        attr = self.getattr(orm, self.column)
        denom = self.getattr(orm, self.denom)
        return attr / denom


## @export
@dataclass
class Column:
    name: str
    title: str = ""  # Title for datatables.net
    read: bool = True  # read this column from data table
    send: bool = True  # send this column to browser
    view: bool = True  # show this column as datatables column
    search: bool = True  # search this column given search query
    aggregate: Aggregate | None = None  # is an aggregate column
    className: str | None = None  # possible className for datatables.net
    denom: str | None = None
    label: str = ""

    def __post_init__(self) -> None:
        if self.title == "":
            self.title = self.name
        if self.label == "":
            self.label = self.name
        if self.aggregate is not None:
            if not isinstance(self.aggregate, Aggregate):  # pragma: no cover
                if "denom" in self.aggregate:
                    self.aggregate = RatioAggregate(**self.aggregate)
                else:
                    self.aggregate = Aggregate(**self.aggregate)
            if self.aggregate.label != self.name:
                self.aggregate = replace(self.aggregate, label=self.name)
            self.search = False
            self.read = False

    def getcolumn(self, orm: type[DeclarativeBase]) -> ColumnElement[Any] | None:
        ret = getattr(orm, self.name, None)
        if ret is None:
            return None
        if self.denom is not None:
            denom = getattr(orm, self.denom, None)
            if denom is None:
                return None
            return (ret / denom).label(self.label)
        if self.label != self.name:
            ret = ret.label(self.label)
        return ret


## @export
class ProteinQuery:
    Join = join(PepProt, Peptide)
    QID = select(PepProt.proteinid).select_from(Join)
    NPRO = select(func.count(PepProt.proteinid.distinct())).select_from(Join)
    COUNT_PROTEIN = select(func.count(Protein.proteinid))
    # NPEP = select(func.count(PepProt.peptideid.distinct())).select_from(Join)
    NPEP = select(func.count(Peptide.peptideid))

    def __init__(
        self,
        peptide_filter: FormFilter | None = None,
        protein_filter: RowFilter
        | RowFilter
        | Sequence[tuple[str, str, Any]]
        | None = None,
        *,
        dtquery: DTQuery | None = None,
        columns: Sequence[Column | str] | None = None,
    ):
        self.dtquery = dtquery
        if isinstance(protein_filter, Sequence):
            protein_filter = RowFilter([RowQuery(*args) for args in protein_filter])

        self.protein_filter = protein_filter.to_sql(Protein) if protein_filter else None
        if peptide_filter is not None:
            self.peptide_filter, prot_where = peptide_filter.calc_where()
            if prot_where is not None:
                self.protein_filter = (
                    and_(prot_where, self.protein_filter)
                    if self.protein_filter is not None
                    else prot_where
                )

        else:
            self.peptide_filter = None
        if columns is None:  # pragma: no cover
            columns = []
        self.columns = [Column(c) if isinstance(c, str) else c for c in columns]

        self.search_columns = [c.name for c in self.columns if c.search]
        self.aggregates = [c.aggregate for c in self.columns if c.aggregate is not None]
        self.protein_columns = (
            [
                attr
                for col in self.columns
                if col.send and col.read
                for attr in [self.getcolumn(col)]
                if attr is not None
            ]
            if self.columns
            else [Protein]  # type: ignore
        )
        self._agg = [self.make_agg(agg) for agg in self.aggregates]

        npro = self.NPRO
        # qid = self.QID
        npep = self.NPEP
        if self.peptide_filter is not None:
            npro = npro.where(self.peptide_filter)  # type: ignore
            # qid = qid.where(self.peptide_filter)  # type: ignore
            npep = npep.where(self.peptide_filter)  # type: ignore
        self.npro = npro
        # self.qid = qid
        self.npep = npep

    def make_agg(self, agg: Aggregate) -> ColumnElement[Any]:
        return agg.make_column(Peptide)

    def protein_in_query(self) -> ColumnElement[Any]:
        assert self.peptide_filter is not None and len(self.aggregates) == 0
        return Protein.proteinid.in_(self.QID.where(self.peptide_filter))

    def peptide_subquery(self) -> Subquery:
        columns = [PepProt.proteinid, *self._agg]
        q = select(*columns).select_from(self.Join)
        if self.peptide_filter is not None:
            q = q.where(self.peptide_filter)
        q = q.group_by(PepProt.proteinid)
        return q.subquery()

    def getcolumn(self, col: Column) -> ColumnElement[Any]:
        attr = col.getcolumn(Protein)
        if attr is None or not hasattr(attr, "property"):
            raise ValueError(
                f"unknown column {col.name} for {Protein.__tablename__} table",
            )
        if isinstance(attr.property, Relationship):
            raise ValueError(f"column {col} is a relationship on protein!")
        return attr

    def build_queries(self) -> tuple[Select[Any], Select[Any]]:
        qid = None
        cols = []
        piq = None
        if self.aggregates:
            qid = self.peptide_subquery()
            cols = qid.columns[1:]
        elif self.peptide_filter is not None:
            piq = self.protein_in_query()

        columns = self.protein_columns + list(cols)

        q: Select[Any] = select(*columns)
        if qid is not None:
            q = q.join(qid, qid.c.proteinid == Protein.proteinid)
        elif piq is not None:
            q = q.where(piq)
        # if self.peptide_filter is not None:
        #     q = q.where(Protein.proteinid.in_(self.qid))
        if self.protein_filter is not None:
            q = q.where(self.protein_filter)

        q, tq = self.process_query(q)
        if qid is not None:
            tq = tq.join(qid, qid.c.proteinid == Protein.proteinid)

        return q, tq

    def query(
        self,
        engine: Engine,
        want_all: bool = True,
    ) -> ProteinQueryResult:
        q, tq = self.build_queries()
        total_proteins = total_peptides = total_filtered = -1
        with engine.begin() as conn:
            if want_all:
                total_proteins = conn.execute(self.npro).scalar() or 0
                total_peptides = conn.execute(self.npep).scalar() or 0
                total_filtered = conn.execute(tq).scalar() or 0
            df = pd.read_sql_query(q, con=conn)
            # sigh! sqllite does not have a std aggregate function
            # so we group_concat and the parse and the string again...
            for a in self.aggregates:
                if a.aggfunc in FAKE_AGGREGATE_FUNCS:
                    df[a.label] = df[a.label].apply(FAKE_AGGREGATE_FUNCS[a.aggfunc])

        return ProteinQueryResult(
            self.rehydrate(df),
            total_proteins,
            total_peptides,
            total_filtered,
        )

    def process_query(self, query: Select[Any]) -> tuple[Select[Any], Select[Any]]:
        q = self.dtquery
        if q:
            if q.search is not None and self.search_columns is not None:
                query = query.where(search_protein_tosql(q.search, self.search_columns))
            if q.order_column is not None:
                col = getattr(Protein, q.order_column, None)
                if col is not None:
                    query = query.order_by(col.asc() if q.ascending else col.desc())
                else:
                    # virtual
                    if q.order_column in {a.label for a in self.aggregates}:
                        asc = "ASC" if q.ascending else "DESC"
                        query = query.order_by(text(f"{q.order_column} {asc}"))

        filtered_total = self.COUNT_PROTEIN
        if query.whereclause is not None:
            filtered_total = filtered_total.where(query.whereclause)

        if q and q.length > 0:
            query = query.slice(q.start, q.start + q.length)
        return query, filtered_total

    def rehydrate(self, df: pd.DataFrame) -> pd.DataFrame:
        return df


## @export
class PeptideQuery:
    Join = join(PepProt, Protein)
    QID = select(PepProt.peptideid).select_from(Join)

    def __init__(
        self,
        peptide_filter: FormFilter | None = None,
        protein_filter: RowFilter | Sequence[tuple[str, str, Any]] | None = None,
        *,
        columns: Sequence[Column | str] | None = None,
        filtered_column: str | None = None,
    ):
        if isinstance(protein_filter, Sequence):
            protein_filter = RowFilter([RowQuery(*args) for args in protein_filter])
        self.protein_filter = protein_filter.to_sql(Protein) if protein_filter else None

        if peptide_filter is not None:
            self.peptide_filter, prot_where = peptide_filter.calc_where()
            if prot_where is not None:
                self.protein_filter = (
                    and_(prot_where, self.protein_filter)
                    if self.protein_filter is not None
                    else prot_where
                )

        else:
            self.peptide_filter = None

        self.filtered_column = filtered_column
        if columns is None:  # pragma: no cover
            columns = []
        self.columns = [Column(c) if isinstance(c, str) else c for c in columns]
        self.aggregates = [c.aggregate for c in self.columns if c.aggregate is not None]
        self._agg = [self.make_agg(c) for c in self.aggregates]
        self.peptide_columns = (
            [
                attr
                for col in self.columns
                if col.read
                for attr in [self.getcolumn(col)]
                if attr is not None
            ]
            if self.columns
            else [Peptide]  # type: ignore
        )

    def getcolumn(self, col: Column) -> ColumnElement[Any] | None:
        if col.aggregate is not None:
            return None
        ret = col.getcolumn(Peptide)
        if ret is None:
            raise ValueError(
                f"unknown column {col.name} for {Peptide.__tablename__} table",
            )
        return ret

    def peptide_in_query(self) -> ColumnElement[Any]:
        assert self.protein_filter is not None
        return Peptide.peptideid.in_(self.QID.where(self.protein_filter))

    def make_agg(self, agg: Aggregate) -> ColumnElement[Any]:
        return agg.make_column(Protein)

    def protein_subquery(self) -> Subquery:
        columns = [PepProt.peptideid, *self._agg]
        q = select(*columns).select_from(self.Join)
        if self.protein_filter is not None:
            q = q.where(self.protein_filter)
        q = q.group_by(PepProt.peptideid)
        return q.subquery()

    def count(self, engine: Engine) -> int:
        q = self.build_query()
        q = select(func.count()).select_from(q.subquery())  # type: ignore
        with engine.connect() as conn:
            return conn.execute(q).scalar_one()

    def build_query(
        self,
    ) -> Select[Any]:
        qid = None
        cols = []
        piq = None
        if self.aggregates:
            qid = self.protein_subquery()
            cols = qid.columns[1:]
        elif self.protein_filter is not None:
            piq = self.peptide_in_query()

        columns = self.peptide_columns + list(cols)

        if self.peptide_filter is not None and self.filtered_column is not None:
            fcol = self.peptide_filter.label(self.filtered_column)
            columns.append(fcol)  # type: ignore

        q: Select[Any] = select(*columns)
        if qid is not None:
            q = q.join(qid, qid.c.peptideid == Peptide.peptideid)
        elif piq is not None:
            q = q.where(piq)
        if self.peptide_filter is not None and self.filtered_column is None:
            q = q.where(self.peptide_filter)
        return q

    def query(
        self,
        engine: Engine,
    ) -> pd.DataFrame:
        q = self.build_query()

        with engine.begin() as conn:
            q = self.process_query(q, conn)
            df = pd.read_sql_query(q, con=conn)
        for a in self.aggregates:
            if a.aggfunc in FAKE_AGGREGATE_FUNCS:
                df[a.label] = df[a.label].apply(FAKE_AGGREGATE_FUNCS[a.aggfunc])
        return self.rehydrate(df)

    def process_query(self, q: Select[Any], conn: Connection) -> Select[Any]:
        return q

    def rehydrate(self, df: pd.DataFrame) -> pd.DataFrame:
        return rehydrate_peptides(df)


## @export
class SimplePeptideQuery:
    def __init__(
        self,
        peptide_filter: RowFilter | Sequence[tuple[str, str, Any]] | None = None,
        extra: FormFilter | None = None,
        *,
        columns: Sequence[Column | str] | None = None,
    ):
        if isinstance(peptide_filter, Sequence):
            peptide_filter = RowFilter([RowQuery(*args) for args in peptide_filter])

        self.peptide_filter = peptide_filter.to_sql(Peptide) if peptide_filter else None
        self.extra = extra
        if columns is None:  # pragma: no cover
            columns = []

        self.columns = [Column(col) if isinstance(col, str) else col for col in columns]

        self.peptide_columns = (
            [self.getcolumn(col) for col in self.columns if col.read]
            if self.columns
            else [Peptide]  # type: ignore
        )

    def getcolumn(self, col: Column) -> ColumnElement[Any]:
        if col.aggregate is not None:
            raise ValueError(f"no aggregate columns permitted: {col.name}")
        ret = col.getcolumn(Peptide)
        if ret is None:
            raise ValueError(
                f"unknown column {col.name} for {Peptide.__tablename__} table",
            )
        return ret

    def build_query(
        self,
    ) -> Select[Any]:
        q: Select[Any] = select(*self.peptide_columns)  # type: ignore

        if self.peptide_filter is not None:
            q = q.where(self.peptide_filter)
        if self.extra is not None:
            wc = self.extra.calc_where()
            if wc.pep_where is not None:
                q = q.where(wc.pep_where)
            # if wc.prot_where is not None:
            #     q = q.where(wc.prot_where)
        return q

    def query(
        self,
        engine: Engine,
    ) -> pd.DataFrame:
        q = self.build_query()
        with engine.connect() as conn:
            df = pd.read_sql_query(q, con=conn)
        return self.rehydrate(df)

    def rehydrate(self, df: pd.DataFrame) -> pd.DataFrame:
        return rehydrate_peptides(df)


## @export
@dataclass
class Stats:
    max_nnls_residual: float = 1.0
    max_maxPeakArea: float = 0.0
    min_enrichment: float = 0.0
    max_enrichment: float = 1.0


def up(v):
    return to_precision(v, 3, shift=1)


def down(v):
    return to_precision(v, 3, shift=-1)


ROUND: dict[str, Callable[[Any], Any]] = {
    "max_nnls_residual": up,
    "min_enrichment": down,
    "max_enrichment": up,
    "max_maxPeakArea": up,
}


## @export
def calc_stats(
    engine: Engine | None,
    round: bool = False,
    scale_intensity: bool = False,
) -> Stats:
    def default(v):  # pragma: no cover
        return to_precision(v, 3)

    if engine is None:  # pragma: no cover
        return Stats()
    if scale_intensity:  # pragma: no cover
        resid = Peptide.nnls_residual / Peptide.totalIntensityWeight
    else:
        resid = Peptide.nnls_residual / Peptide.totalNNLSWeight
    q = select(
        func.max(resid).label("max_nnls_residual"),
        func.max(Peptide.maxPeakArea).label("max_maxPeakArea"),
        func.min(Peptide.enrichment).label("min_enrichment"),
        func.max(Peptide.enrichment).label("max_enrichment"),
    )
    with engine.connect() as conn:
        row = conn.execute(q).mappings().one()
    if round:
        d = {k: ROUND.get(k, default)(v) for k, v in row.items()}
    else:
        d = dict(row)
    return Stats(**d)


## @export
def sqlite_version(engine: Engine | Path) -> int:
    from .model import Version

    dispose = False
    if isinstance(engine, Path):  # pragma: no cover
        engine = file2engine(engine)
        dispose = True

    q = select(
        func.max(Version.version).label(
            "version",
        ),
    )
    try:
        with engine.connect() as conn:
            row = conn.execute(q).mappings().one_or_none()
            if row is None:
                return -1
            return row["version"]
    except OperationalError:
        return 0
    finally:
        if dispose:
            engine.dispose()


def db_columns(engine: Engine | Path) -> tuple[list[str], list[str]]:
    from sqlalchemy import MetaData

    if isinstance(engine, Path):  # pragma: no cover
        engine = file2engine(engine)
    m = MetaData()
    try:
        m.reflect(only=["peptides", "proteins"], bind=engine)
        pep = m.tables["peptides"]
        prot = m.tables["proteins"]
        return [c.name for c in pep.columns], [c.name for c in prot.columns]

    except OperationalError:  # pragma: no cover
        return [], []
