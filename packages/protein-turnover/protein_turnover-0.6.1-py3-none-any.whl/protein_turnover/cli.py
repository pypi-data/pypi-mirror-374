from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import click

# from click_didyoumean import DYMGroup

HIDDEN = os.environ.get("TURNOVER_FULL", "0") != "1"
IsFile = click.Path(dir_okay=False, file_okay=True)

CONFIG = Path("~/.turnover.toml").expanduser()


@dataclass
class Config:
    logfile: str | None = None
    loglevel: str | None = None
    user_config: str | None = None


pass_config = click.make_pass_decorator(Config, ensure=True)


def update_mailhost(mailhost: str) -> None:
    from . import config

    config.MAIL_SERVER = mailhost


def update_config(filename: str | Path) -> None:
    from . import config
    import tomllib

    try:
        with open(filename, "rb") as fp:
            d = tomllib.load(fp)
    except Exception as e:
        raise click.BadParameter(
            f"can't read configuration file: {e}",
            param_hint="config",
        )

    for k, v in d.items():
        if k == "website":
            continue
        k = k.upper()
        if hasattr(config, k):
            setattr(config, k, v)
        else:
            click.secho(f"unknown configuration attribute {k}", fg="red")


epilog = click.style("turnover commands\n", fg="magenta")

epilog = f"""{epilog}

If no `--config` file is supplied `turnover` checks for a default configuration
file at `~/.turnover.toml` (see `init-config` to make one).
"""


@click.group(epilog=epilog)
@click.option(
    "-l",
    "--level",
    type=click.Choice(
        ["info", "debug", "warning", "error", "critical"],
        case_sensitive=False,
    ),
    help="log level",
)
@click.option(
    "-f",
    "--logfile",
    type=click.Path(file_okay=True, dir_okay=False),
    help="log file to write to (use '-' to log to stderr)",
)
@click.option(
    "-m",
    "--mailhost",
    help="where to send emails to",
    metavar="HOST",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(file_okay=True, dir_okay=False, exists=True),
    help="configuration file for turnover [.TOML format]",
)
@click.version_option()
@click.pass_context
def cli(
    ctx: click.Context,
    level: str | None,
    logfile: str | None = None,
    config: str | None = None,
    mailhost: str | None = None,
) -> None:
    from .logger import init_logger

    ctx.obj = Config(
        logfile=logfile,
        loglevel=level,
        user_config=config,
    )
    if level is None:
        level = "WARNING"

    if config is not None:
        update_config(config)
    else:
        if CONFIG.exists():
            update_config(CONFIG)
    if mailhost is not None:
        update_mailhost(mailhost)

    init_logger(level=level, logfile=logfile)
