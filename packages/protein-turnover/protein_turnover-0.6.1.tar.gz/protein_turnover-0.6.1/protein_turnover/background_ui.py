from __future__ import annotations

import click

from .cli import cli
from .cli import Config
from .cli import pass_config


@cli.command(name="background")
@click.option(
    "--workers",
    type=int,
    help="number of workers [default - half the number of cpus]",
)
@click.option(
    "--nice",
    default=0,
    type=click.IntRange(
        min=0,
    ),
    help="run turnover command at this nice level",
)
@click.option(
    "--sleep",
    default=60.0,
    help="sleep (seconds) between directory scans",
    show_default=True,
)
@click.option(
    "--run-config",
    type=click.Path(file_okay=True, dir_okay=False, exists=True),
    help="configuration file to pass off to the background process",
)
@click.option(
    "--mailhost",
    help='send emails to this mailhost. use "none" for no emails',
    hidden=False,
)  # see runner.py
@click.argument(
    "directory",
    type=click.Path(dir_okay=True, exists=True, file_okay=False),
)
@pass_config
def background_cmd(
    cfg: Config,
    directory: str,
    workers: int | None,
    run_config: str | None,
    sleep: float,
    nice: int,
    mailhost: str | None = None,
) -> None:  # pragma: no cover
    """Watch and run turnover jobs from directory"""
    from os import cpu_count
    from .background import SimpleQueue
    from .logger import logger

    if workers is None:
        workers = max((cpu_count() or 1) // 2, 1)
        logger.warning("using %d workers", workers)

    squeue = SimpleQueue(
        directory,
        workers=workers,
        wait=sleep,
        nice=nice,
        config=run_config or cfg.user_config,
        mailhost=mailhost,
    )
    squeue.run()
