from __future__ import annotations

from pathlib import Path

import click

from ..cli import cli
from ..cli import HIDDEN


@cli.group(help=click.style("add sqlite columns", fg="magenta"), hidden=HIDDEN)
def fix() -> None:
    pass


def show(filename: str, *, echo: bool = False) -> None:
    from .model import file2engine
    from .model import Peptide
    from sqlalchemy import select

    engine = file2engine(filename, echo=echo)

    with engine.connect() as conn:
        res = conn.execute(
            select(
                Peptide.iso_peaks_nr_20,
                Peptide.iso_peaks_nr_40,
                Peptide.iso_peaks_nr_60,
                Peptide.iso_peaks_nr_80,
            )
            .select_from(Peptide)
            .limit(10),
        )
        for r in res.all():
            print(
                r.iso_peaks_nr_20,
                r.iso_peaks_nr_40,
                r.iso_peaks_nr_80,
                r.iso_peaks_nr_80,
            )


@fix.command()
@click.option("--force", is_flag=True, help="redo computations")
@click.option("--echo", is_flag=True, help="echo sql commands")
@click.argument(
    "directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
def fixall(directory: str, force: bool, echo: bool) -> None:
    """Fix all .sqlite files in a directory tree"""
    import os
    from .iso_peaks import fixsqlite

    for root, _dirs, files in os.walk(directory):
        for f in files:
            if not f.endswith(".sqlite"):
                continue
            path = os.path.join(root, f)
            ret = fixsqlite(path, force=force, echo=echo)
            click.secho(
                f"{'fixed' if ret else 'ok'}: {path}",
                fg="yellow" if ret else "green",
            )


@fix.command(name="fixsqlite")
@click.option("--force", is_flag=True, help="redo computations")
@click.option("--echo", is_flag=True, help="echo sql commands")
@click.argument(
    "filename",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
def _fixsqlite(filename: str, force: bool, echo: bool) -> None:
    """Fix a single sqlite file"""
    from .iso_peaks import fixsqlite

    ret = fixsqlite(filename, force=force, echo=echo)
    if ret:
        click.secho(f"added columns: {','.join(ret)}", fg="yellow")
    show(filename, echo=echo)


@fix.command()
@click.option("--echo", is_flag=True, help="echo sql commands")
@click.option("--regex", is_flag=True, help="match as regex")
@click.argument(
    "filename",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.argument("column", nargs=-1)
def drop(filename: str, column: tuple[str, ...], echo: bool, regex: bool) -> None:
    """drop columns in a single sqlite file"""
    from .iso_peaks import dropif_pep_columns
    from .model import file2engine

    path = Path(filename).absolute()
    if not path.exists():
        return
    engine = file2engine(filename, echo=echo)

    cols = dropif_pep_columns(engine, list(column), regex=regex)
    if cols:
        click.secho(f"dropped {', '.join(cols)}", fg="green")


@fix.command()
@click.option("--echo", is_flag=True, help="echo sql commands")
@click.option("--regex", is_flag=True, help="match as regex")
@click.argument(
    "directory",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.argument("column", nargs=-1)
def dropall(directory: str, column: tuple[str, ...], echo: bool, regex: bool) -> None:
    """drop columns for all .sqlite files in a directory"""
    import os
    from .iso_peaks import dropif_pep_columns
    from .model import file2engine

    if not column:
        return

    for root, _dirs, files in os.walk(directory):
        for f in files:
            if not f.endswith(".sqlite"):
                continue
            path = os.path.join(root, f)
            engine = file2engine(path, echo=echo)
            cols = dropif_pep_columns(engine, list(column), regex=regex)
            if cols:
                click.secho(f"{path}: dropped {', '.join(cols)}", fg="green")
