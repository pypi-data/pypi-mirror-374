from __future__ import annotations

from typing import Any
from typing import Callable
from typing import Literal

import click

from .cli import cli
from .cli import CONFIG
from .cli import Config
from .cli import pass_config


def web_options(f: Callable) -> Callable:
    f = click.option(
        "-s",
        "--server",
        type=click.Choice(["gunicorn", "waitress", "flask"]),
        help="which wsgi server to run",
    )(f)
    f = click.option(
        "-n",
        "--no-browse",
        is_flag=True,
        help="don't open web application in browser",
    )(f)
    f = click.option(
        "--port",
        default=8000,
        help="port to run webservice on",
        show_default=True,
    )(f)

    return f


WebServer = Literal["flask", "gunicorn", "waitress"]


@cli.command(
    epilog="""

Running a webserver + turnover backend.

If not specifed with options or in a configuration file.
job results will be stored in `~/turnover_jobs` (created if not existing)
and file caches will use `~/turnover_cache` (created in not existing).

\b
Configuration
=============

If a configuration file is specified then you can specifiy
JOBSDIR, CACHEDIR.

The program will look for a file `~/.turnover.toml` for website
configuration if no `--web-config` is given.

Run `turnover web` and browse to "Configuration" for more information.

You can give arguments to the underlying webserver with arguments after
a `--`, e.g.:

`turnover web --server=gunicorn --workers=4 -- --workers=2`

will tell gunicorn to fire up 2 workers and use 4 background workers for turnover itself.
""",
)
@click.option(
    "-w",
    "--workers",
    type=int,
    help="number of background workers [default: half the number of cpus]",
)
@web_options
@click.option(
    "-c",
    "--web-config",
    type=click.Path(file_okay=True, dir_okay=False, exists=True),
    help="configuration file for web browser",
)
@click.option(
    "--jobs-dir",
    type=click.Path(file_okay=False),
    help="directory to run job [default: directory of ~/turnover_jobs]",
)
@click.option(
    "--cache-dir",
    type=click.Path(file_okay=False),
    help="directory to store file caches [default: directory of ~/turnover_cache]",
)
@click.option(
    "-v",
    "--view-only",
    is_flag=True,
    help="only view data",
)
@click.option(
    "--mailhost",
    help="specify MAILHOST to allow background jobs to email user when done. Default is to not send emails",
    default="none",
)
@click.argument("server_options", nargs=-1)
@pass_config
def web(
    cfg: Config,
    no_browse: bool,
    workers: int,
    web_config: str | None,
    server: WebServer | None = None,
    jobs_dir: str | None = None,
    cache_dir: str | None = None,
    port: int = 8000,
    server_options: tuple[str, ...] = (),
    view_only: bool = False,
    mailhost: str | None = None,
) -> None:  # pragma: no cover
    """Run full website (requires protein-turnover-website)."""
    from os import cpu_count
    from .web import WebRunner

    if workers is None:
        workers = max((cpu_count() or 1) // 2, 1)
    defaults: dict[str, Any] = {}
    if cache_dir is not None:
        defaults["CACHEDIR"] = cache_dir

    if jobs_dir is not None:
        defaults["JOBSDIR"] = [jobs_dir]
    wr = WebRunner(
        browse=not no_browse,
        workers=workers,
        web_config=web_config,
        server=server,
        configfile=cfg.user_config,
        defaults=defaults,
        port=port,
        server_options=server_options,
        view_only=view_only,
        mailhost=mailhost,
    )

    wr.run()


@cli.command()
@web_options
@click.argument("jobfile", type=click.Path(file_okay=True, exists=True, dir_okay=False))
@click.argument("server_options", nargs=-1)
@pass_config
def view(
    cfg: Config,
    no_browse: bool,
    jobfile: str,
    server: WebServer | None = None,
    port: int = 8000,
    server_options: tuple[str, ...] = (),
) -> None:  # pragma: no cover
    """View a completed run in a browser (requires protein-turnover-website)"""
    from pathlib import Path
    from .web import WebRunner
    from .jobs import TurnoverJob
    from .resourcefiles import ResultsResourceFile

    jf = Path(jobfile).expanduser().resolve()
    if not jf.exists():
        click.secho(f"no such file {jobfile}", fg="red")
        raise click.Abort()

    try:
        job = TurnoverJob.restore(jf)
    except Exception as e:
        click.secho(
            f'Can\'t read "{jf.name}" as a TOML file: {e}',
            fg="red",
            bold=True,
            err=True,
        )
        raise click.Abort()
    jobsddir = jf.parent
    if job.auto_generated_jobid:
        results = ResultsResourceFile(job.jobid, jobsddir)
        if not results.has_result():
            raise ValueError(f"can't find output data file {results.cache_result()}")
    dataid = jf.stem
    defaults = {"JOBSDIR": [str(jobsddir)], "DATAID": f"0---{dataid}"}

    wr = WebRunner(
        browse=not no_browse,
        workers=1,
        web_config=None,
        server=server,
        configfile=cfg.user_config,
        defaults=defaults,
        port=port,
        view_only=True,
        wsgi_app="protein_turnover_website.wsgi_view",
        server_options=server_options,
        mailhost="none",
    )

    wr.run()


@cli.command(hidden=True)
@web_options
@click.argument("server_options", nargs=-1)
@pass_config
def config(
    cfg: Config,
    no_browse: bool,
    server: WebServer | None = None,
    port: int = 8000,
    server_options: tuple[str, ...] = (),
) -> None:
    """View Configuration information"""
    from .web import WebRunner

    wr = WebRunner(
        browse=not no_browse,
        workers=1,
        web_config=None,
        defaults={"DATAID": "noid"},
        server=server,
        port=port,
        # extra=web_options,
        view_only=True,
        wsgi_app="protein_turnover_website.wsgi_view",
        page="configuration.html",
        server_options=server_options,
        mailhost="none",
    )
    wr.run()


@cli.command()
@click.option(
    "-o",
    "--out",
    type=click.Path(dir_okay=False),
    help="write configuration file here [default ~/.turnover.toml]",
)
@click.option("--force", is_flag=True, help="force overwriting of any existing file")
@click.option("--without-website", is_flag=True, help="don't add website configuration")
def init_config(force: bool, without_website: bool, out: str | None) -> None:
    """Create a default configuration file"""
    from pathlib import Path

    from .web import has_package, dump_config

    if out is None:
        configfile = CONFIG
    else:
        configfile = Path(out)

    if configfile.exists() and not force:
        click.secho(f"{configfile} file exists! Use --force to overwrite.")
        return
    if not without_website and not has_package("protein_turnover_website"):
        click.secho(
            "Please install protein_turnover_website for website config [pip install protein-turnover-website]!",
            fg="red",
            err=True,
        )
        raise click.Abort()

    dump_config(configfile, not without_website)
