from __future__ import annotations

from pathlib import Path
from typing import Callable
from typing import TYPE_CHECKING

import click

from .cli import cli
from .cli import Config
from .cli import IsFile
from .cli import pass_config
from .settings import setting_options

if TYPE_CHECKING:
    from .utils import PeptideSettings


@cli.command(name="mzi-create", hidden=False)
@click.option("--force", is_flag=True, help="force creation")
@click.option(
    "-w",
    "--workers",
    type=int,
    help="number of background workers [default: half number of cpus]",
)
@click.option(
    "-o",
    "--out",
    help="directory to write [default is directory of mzML file]",
    type=click.Path(dir_okay=True, file_okay=False),
)
@click.argument("mzmlfiles", nargs=-1, type=IsFile)
def mzml_create_cmd(
    mzmlfiles: tuple[str, ...],
    out: str | None,
    workers: int | None,
    force: bool = False,
) -> None:
    """Create mz/intensity memory mapped files for mzML files"""

    from functools import partial
    from os import cpu_count

    from .resourcefiles import MzMLResourceFileLocal
    from .parallel_utils import parallel_result
    from .pymz import mzml_create
    from .logger import logger

    if workers is None:
        workers = max((cpu_count() or 1) // 2, 1)

    targets = [MzMLResourceFileLocal(m, out) for m in set(mzmlfiles)]
    todo = [t for t in targets if not t.cache_mzml_ok()] if not force else targets
    skipped = set(targets) - set(todo)
    if skipped:  # pragma: no cover
        for t in skipped:
            logger.info("skipping creation of %s cache", t.original.name)
    if not todo:
        return
    if out is not None:
        pout = Path(out)
        if not pout.exists():  # pragma: no cover
            pout.mkdir(parents=True, exist_ok=True)

    exe: list[Callable[[], int]] = []
    for idx, target in enumerate(todo, start=1):
        exe.append(partial(mzml_create, target, idx, len(todo)))

    ntotal = len(exe)

    for idx, _ in enumerate(parallel_result(exe, workers=workers), start=1):
        logger.info("mzml prepare task done: [%d/%d]", idx, ntotal)


@cli.command(name="run")
@click.option(
    "-w",
    "--workers",
    type=int,
    help="number of parallel workers [default: half the number of cpus]",
)
@click.option(
    "--nspectra",
    type=int,
    help="split tasks into this many spectra (see NSPECTRA configuration variable)",
)
@click.option(
    "--job-dir",
    type=click.Path(file_okay=False),
    help="directory to run job (where output files will be placed) [default: directory of jobfile]",
)
@click.option(
    "--cache-dir",
    type=click.Path(file_okay=False),
    help="directory to store cache files [default: cache_dir specified in jobfile]",
)
@click.option("--force", is_flag=True, help="force (re)creation of cache files")
@click.option(
    "--mailhost",
    help='send emails to this mailhost. Use "none" for send no emails',
)  # see runner.py
@click.option(
    "--no-cleanup",
    is_flag=True,
    help="don't clean up auxillary DataFrame files",
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    help="be quiet... don't log anything above WARNING",
)
@click.option(
    "--testing",
    type=int,
    help="we are testing... set the number of pepxml rows to use",
    hidden=True,
)
@click.option(
    "--interrupt-as-error",
    default=0,
    help="accept keyboard interrupt as error. Value will be exit code",
    hidden=True,  # only useful to for background process: see runner.py
)  # see runner.py
@click.argument("job")
@pass_config
def turnover_job_run_cmd(
    cfg: Config,
    job: str | Path,
    force: bool = False,
    workers: int | None = None,
    nspectra: int | None = None,
    job_dir: str | Path | None = None,
    interrupt_as_error: int = 0,
    mailhost: str | None = None,
    cache_dir: str | None = None,
    no_cleanup: bool = False,
    quiet: bool = False,
    testing: int | None = None,
) -> None:
    """Run a turnover job"""
    from dataclasses import replace
    from os import cpu_count
    from .pymz import turnover_run, turnover_prepare
    from .resourcefiles import ResultsResourceFile

    from .logger import init_logger, logger
    from .jobs import TurnoverJob
    from .config import NSPECTRA, INSPECT_URL, MAIL_TEXT, MAIL_TIMEOUT

    if nspectra is None:
        nspectra = NSPECTRA

    if workers is None:
        workers = max((cpu_count() or 1) // 2, 1)

    def maybeemail(template: str | None, url: str | None = None) -> None:
        if mailhost != "none" and jobby.email and template:
            from .mailer import sendmail

            if mailhost is None:
                from .config import MAIL_SERVER

                lmailhost = MAIL_SERVER
            else:
                lmailhost = mailhost

            if url:
                try:
                    url = url.format(jobid=jobby.jobid)
                    url = f' <a href="{url}">See results</a>'
                except KeyError:
                    url = ""
            else:
                url = ""
            msg = template.format(job=jobby, url=url)

            try:
                sendmail(
                    msg,
                    jobby.email,
                    mimetype="html",
                    mailhost=lmailhost,
                    timeout=MAIL_TIMEOUT,
                )
            except OSError as e:
                logger.warning("failed to send email to %s: reason %s", jobby.email, e)

    job = Path(job)
    jobby = TurnoverJob.restore(job)
    save_job = False
    if job_dir is None:
        job_dir = job.parent
        if jobby.jobid != job.stem:
            save_job = True
    else:
        job_dir = Path(job_dir)
        if interrupt_as_error == 0:
            save_job = True  # save a copy of the job toml file

    if cache_dir is not None:
        jobby = replace(jobby, cache_dir=cache_dir)

    job_dir.mkdir(exist_ok=True, parents=True)

    level: str | int = "INFO" if cfg.loglevel is None else logger.getEffectiveLevel()
    if quiet:
        level = "WARNING"
    logfile: str | Path | None
    if cfg.logfile is None and interrupt_as_error > 0:
        # this is a background job and no logfile has been specified
        logfile = job_dir / f"{jobby.jobid}.log"
    else:
        logfile = cfg.logfile
    # only reinit if we haven't specified logfile
    init_logger(level=level, logfile=logfile, reinit=cfg.logfile is None)

    # lock the cache directories so we don't delete anything until results done
    # we assume the job dirctory is never deleted
    rf = jobby.to_resource_files()
    results = ResultsResourceFile(
        jobby.jobid,  # output filenames will be e.g. {jobid}.sqlite
        job_dir,
    )
    try:
        rf.ensure_directories()
        rf.lock()
        turnover_prepare(rf, force=force, workers=workers)

        turnover_run(
            jobby,
            results,  # where to store stuff for this job
            workers=workers,
            nspectra=nspectra,
            save_subset=True,
            cleanup=not no_cleanup,
            save_job=save_job,
            testing=testing,
        )
        # interrupt as_error != 0 means we are running as the
        # background job for the website.
        if interrupt_as_error:
            jobby = replace(jobby, status="finished")
            jobby.save_to_dir(job_dir)  # save a copy of the job
    except Exception as e:  # pragma: no cover
        results.cleanup()
        logger.error("turnover %s failed. reason: %s", jobby.jobid, e)
        maybeemail('Protein Turnover Job "{job.job_name}" has <b>failed</b>!')
        raise e
    except KeyboardInterrupt as e:  # pragma: no cover
        results.cleanup()
        if interrupt_as_error:
            logger.error("turnover %s killed", jobby.jobid)
            raise SystemExit(interrupt_as_error) from e
        raise e
    finally:
        rf.unlock()

    maybeemail(MAIL_TEXT, INSPECT_URL)


@cli.command(name="job")
@click.option(
    "-o",
    "--out",
    help="filename to write file to",
    type=click.Path(dir_okay=False, file_okay=True),
)
@click.option("-j", "--jobid", help="job id")
@click.option("-n", "--name", help="job name")
@click.option(
    "-x",
    "--no-check",
    is_flag=True,
    help="don't do any sanity checks on the files",
)
@click.argument("pepxml", type=IsFile)
@click.argument("protxml", type=IsFile)
@click.argument("mzmlfiles", nargs=-1, type=IsFile)
@setting_options
def turnover_job(
    pepxml: str,
    protxml: str,
    mzmlfiles: list[str],
    no_check: bool,
    name: str | None,
    jobid: str | None,
    settings: PeptideSettings,
    out: str | None = None,
) -> None:
    """Create a turnover job file"""
    from .jobs import TurnoverJob, jobidkey
    from .pepxml import scan_spectra
    from .protxml import scan_proteins
    from .pymz import scan_mzml_spectra
    from .jobs import slugify

    if not no_check:
        missing = []
        for f in [pepxml, protxml, *mzmlfiles]:
            if not Path(f).exists():
                missing.append(f)
        if missing:
            click.secho(
                f"These are not files: {', '.join(missing)}",
                fg="red",
                err=True,
            )
            raise click.Abort()

        n = sum(1 for _ in scan_spectra(Path(pepxml)))
        if n == 0:
            raise click.BadParameter(
                f"peptide XML {pepxml} has no spectra",
                param_hint="pepxml",
            )
        mzmlfiles = list(set(mzmlfiles))
        n = sum(1 for _ in scan_proteins(Path(protxml)))
        if n == 0:
            raise click.BadParameter(
                f"protein XML {protxml} has no proteins",
                param_hint="protxml",
            )
        failed = []
        for mzml in mzmlfiles:
            n = sum(1 for _ in scan_mzml_spectra(Path(mzml)))
            if n == 0:
                failed.append(mzml)
        if failed:
            raise click.BadParameter(
                f'mzML "{", ".join(failed)}" has no spectra',
                param_hint="mzmlfiles",
            )

    if not jobid:
        if name:
            jobid = slugify(name)
        if not jobid or len(jobid) < 4:
            jobid = jobidkey(pepxml, protxml, mzmlfiles)

    job_name = name or jobid

    if out is None:
        filename = Path(f"{jobid}.toml")
    else:
        filename = Path(out)
    if not filename.parent.exists():
        filename.parent.mkdir(parents=True, exist_ok=True)

    job = TurnoverJob(
        job_name=job_name,
        pepxml=[pepxml],
        protxml=protxml,
        mzmlfiles=mzmlfiles,
        # cache_dir=str(filename.parent),
        jobid=jobid,
        settings=settings,
    )

    # if not no_check:
    #     msg = job.verify()
    #     if msg is not None:
    #         click.secho(f"{msg}", fg="red", err=True, bold=True)
    #         raise click.Abort()

    jobfile = job.save_to_dir(filename.parent, filename.name)
    click.secho(f'written job to "{jobfile}"', fg="yellow")


@cli.command(name="prepare", hidden=True)
@click.option(
    "-c",
    "--cache-dir",
    help="cache directory to use",
    type=click.Path(dir_okay=True, file_okay=False),
)
@click.option("--force", is_flag=True, help="force creation")
@click.argument("job", type=IsFile)
def turnover_job_prepare(
    job: str,
    cache_dir: str | None,
    force: bool = False,
) -> None:
    """Prepare pepXML and mzML cache files"""
    from dataclasses import replace
    from .jobs import TurnoverJob
    from .pymz import turnover_prepare

    jobby = TurnoverJob.restore(job)
    if cache_dir is not None:
        jobby = replace(jobby, cache_dir=cache_dir)

    rf = jobby.to_resource_files()
    turnover_prepare(
        rf,
        force=force,
    )


@cli.command(hidden=True)
@click.option("--verbose", is_flag=True, help="show more data")
@click.argument("filenames", nargs=-1, type=IsFile)
def hash(filenames: list[str], verbose: bool) -> None:  # pragma: no cover
    "Calculate sha256 hashes from files"
    from datetime import datetime
    from .utils import human
    from .resourcefiles import hash256

    for name in [Path(n) for n in set(filenames)]:
        s = datetime.now()
        h = hash256(name)
        e = datetime.now()

        if verbose:
            size = name.stat().st_size
            dt = e - s
            bs = int(size / dt.total_seconds())
            click.echo(f"{h} [{dt}]: {human(size):>8}: {human(bs):>8}/s {name}")
        else:
            click.echo(f"{h} {name}")
