from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
from sqlalchemy import MetaData
from sqlalchemy import select
from sqlalchemy import text
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from .model import Peptide
from .utils import file2engine


def get_pepitde_cols(engine: Engine) -> list[str]:
    """Get *actual* list of column names for peptides table."""
    assert engine.url.drivername == "sqlite", engine.url
    q = text(f"PRAGMA table_info({Peptide.__tablename__})")
    with engine.connect() as conn:
        tcols = conn.execute(q).all()
        return [row[1] for row in tcols]


def get_pepitde_cols2(engine: Engine) -> list[str]:
    """Get *actual* list of column names for peptides table."""
    m = MetaData()
    m.reflect(bind=engine, only=[Peptide.__tablename__])
    pep = m.tables[Peptide.__tablename__]
    return [c.name for c in pep.columns]


def add_pep_columns(engine: Engine, cols: list[str]) -> None:
    """Add columns to peptides table."""
    tablename = Peptide.__tablename__
    q = "ALTER TABLE {tablename} add {col} INTEGER NOT NULL DEFAULT 0"
    with engine.connect() as conn:
        for col in cols:
            conn.execute(text(q.format(col=col, tablename=tablename)))
        conn.commit()


def drop_pep_columns(engine: Engine, cols: list[str]) -> None:
    """Drop columns to peptides table."""
    tablename = Peptide.__tablename__
    q = "ALTER TABLE {tablename} DROP COLUMN {col}"
    with engine.connect() as conn:
        for col in cols:
            conn.execute(text(q.format(col=col, tablename=tablename)))
        conn.commit()


def addif_pep_columns(engine: Engine, cols: list[str]) -> list[str]:
    """Add columns that don't exist in peptides table."""
    rcols = get_pepitde_cols(engine)
    cols = list(set(cols) - set(rcols))
    if cols:
        add_pep_columns(engine, cols)
    return cols


def dropif_pep_columns(
    engine: Engine,
    cols: list[str],
    *,
    regex: bool = False,
) -> list[str]:
    """Remove columns that exist in peptides table."""
    rcols = get_pepitde_cols(engine)
    if regex:
        xcols = set()
        for cc in rcols:
            for c in cols:
                if re.match(c, cc) is not None:
                    xcols.add(cc)
                    break
        cols = list(xcols)
    else:
        cols = list(set(cols) - set(rcols))
    if cols:
        drop_pep_columns(engine, cols)
    return cols


def isoPeakNr(arr: list[float] | None, isoPeaksMinRSQ: float) -> int:
    if not arr:
        return 0
    return int(np.sum(np.array(arr[2:]) >= isoPeaksMinRSQ))  # need this int()!


def populate_isoPeaksNr(
    engine: Engine,
    cols: list[tuple[str, float]],
    force: bool = False,
) -> list[str]:
    rcols = addif_pep_columns(engine, [c[0] for c in cols])
    if not rcols and not force:
        return rcols
    q = select(Peptide.peptideid, Peptide.adjustedRsq)
    with engine.connect() as conn:
        res = conn.execute(q).all()

    Session = sessionmaker()
    # see "ORM Bulk UPDATE by Primary Key"
    # https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-bulk-update-by-primary-key

    with Session(bind=engine) as session:
        for col, isoPeaksMinRSQ in cols:
            u = [
                {"peptideid": peptideid, col: isoPeakNr(adjustedRsq, isoPeaksMinRSQ)}
                for (peptideid, adjustedRsq) in res
            ]
            session.execute(update(Peptide), u)

        session.commit()

    return rcols


def isoPeaksMinRSQToI(r2: float) -> int:
    return int(r2 * 100)


def gen_cols() -> list[tuple[str, float]]:
    from .model import MINRSQ100

    return [(f"iso_peaks_nr_{n}", n / 100.0) for n in MINRSQ100]


def populate_isoPeaksNrFixed(
    engine: Engine,
    force: bool = False,
) -> list[str]:
    return populate_isoPeaksNr(
        engine,
        gen_cols(),
        force=force,
    )


## @export
def fixsqlite(
    filename: str | Path,
    *,
    force: bool = False,
    echo: bool = False,
) -> list[str]:
    path = Path(filename)
    if not path.exists():
        return []
    engine = file2engine(filename, echo=echo)
    try:
        return populate_isoPeaksNrFixed(engine, force=force)
    finally:
        engine.dispose()


def to_nr(arr: list[float], cols: list[tuple[str, float]]) -> pd.Series:
    if not arr:
        return pd.Series({col: 0 for col, _ in cols})
    a = np.array(arr)
    return pd.Series(
        {
            col: int(np.sum(np.array(a[2:]) >= isoPeaksMinRSQ))
            for col, isoPeaksMinRSQ in cols
        },
    )


def add_iso_peaks(pep_df: pd.DataFrame) -> pd.DataFrame:
    rsq = pep_df["adjustedRsq"]

    edf = rsq.apply(to_nr, args=(gen_cols(),))
    return pd.concat([pep_df, edf], axis=1)
