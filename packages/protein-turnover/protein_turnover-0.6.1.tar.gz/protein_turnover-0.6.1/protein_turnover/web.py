from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from types import ModuleType
from typing import Any
from typing import Callable
from typing import Literal
from typing import TypedDict

import click
import tomli_w
from typing_extensions import NotRequired
from typing_extensions import override

from .background import Processing
from .cli import CONFIG


class PopenArgs(TypedDict):
    process_group: NotRequired[int | None]
    creationflags: int
    preexec_fn: Callable[[], None] | None


@dataclass
class Runner:
    name: str
    cmd: list[str]
    directory: str = "."
    env: dict[str, str] | None = None
    showcmd: bool = False
    shell: bool = False
    prevent_sig: bool = False  # prevent Cntrl-C from propagating to child process

    def getenv(self) -> dict[str, str] | None:
        if not self.env:
            return None
        return {**os.environ, **self.env}

    def start(self) -> subprocess.Popen[bytes]:
        if self.showcmd:
            click.secho(" ".join(str(s) for s in self.cmd), fg="blue")

        kwargs = PopenArgs(creationflags=0, preexec_fn=None)
        if self.prevent_sig:
            self.set_new_process_group(kwargs)
        return subprocess.Popen(  # type: ignore
            self.cmd,
            cwd=self.directory,
            env=self.getenv(),
            shell=self.shell,
            **kwargs,
        )

    def set_new_process_group(self, kwargs: PopenArgs) -> None:
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            if sys.version_info >= (3, 11):
                kwargs["process_group"] = 0
            else:
                kwargs["preexec_fn"] = os.setpgrp


def browser(  # pragma: no cover
    url: str = "http://127.0.0.1:8000",
    sleep: float = 5.0,
) -> Thread:
    import webbrowser

    def run() -> None:
        time.sleep(sleep)
        webbrowser.open_new_tab(url)

    tr = Thread(target=run)
    tr.daemon = True  # exit when main process exits
    tr.start()
    return tr


def has_package(package: str) -> bool:
    return get_package(package) is not None


def get_package(package: str) -> ModuleType | None:
    import importlib

    try:
        return importlib.import_module(package)

    except ModuleNotFoundError:  # pragma: no cover
        return None


def default_conf() -> dict[str, Any]:
    # from tempfile import gettempdir

    conf = {
        "MOUNTPOINTS": [
            ("~", "HOME"),
        ],
        "JOBSDIR": ["~/turnover_jobs"],
        "CACHEDIR": "~/turnover_cache",
        "WEBSITE_STATE": "single_user",
    }
    return conf


def instance_conf(config: Path | str, ns: str | None = None) -> dict[str, Any]:
    # """We *must* have flask in our environment by now"""
    # from flask import Config  # pylint: disable=import-error
    # conf = Config(".")
    # conf.from_pyfile(config)
    # return conf
    try:
        with open(config, "rb") as fp:
            ret = tomllib.load(fp)
            if ns is not None:
                ret2 = ret.get(ns, None)
                return ret2 or {}
            return ret
    except tomllib.TOMLDecodeError as e:  # pragma: no cover
        raise click.BadParameter(
            f'Can\'t parse configuration file "{config}": {e}',
        ) from e


def dump_config(configfile: Path, with_website: bool) -> None:
    from . import config

    def mod2dict(module: ModuleType) -> dict[str, Any]:
        d: dict[str, Any] = {}
        for k in dir(module):
            if k.isupper():
                a = getattr(module, k)
                if a is None:
                    # a = ""
                    continue
                d[k] = a

        d = dict(sorted(d.items()))
        return d

    HEADER = b"""# turnover configuration file.
# Remove/comment out any values you don't change since these are defaults.
"""
    d = mod2dict(config)
    if with_website:
        c = get_package("protein_turnover_website.config")
        assert c is not None
        d["website"] = mod2dict(c)

    click.secho(f"writing: {configfile}")
    with open(configfile, "wb") as fp:
        fp.write(HEADER)
        tomli_w.dump(d, fp)


def waitress_app(wsgi_app: str, port: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "waitress",
        f"--listen=127.0.0.1:{port}",
        wsgi_app + ":application",
    ]


def flask_app(wsgi_app: str, port: int) -> list[str]:
    return [sys.executable, "-m", "flask", "--app", wsgi_app, "run", f"--port={port}"]


def gunicorn_app(wsgi_app: str, port: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "gunicorn",
        f"--bind=127.0.0.1:{port}",
        wsgi_app,
    ]


APPS = {"gunicorn": gunicorn_app, "waitress": waitress_app, "flask": flask_app}

WebServer = Literal["flask", "gunicorn", "waitress"]


@dataclass(kw_only=True)
class WebRunner:
    browse: bool = False
    workers: int = 1
    web_config: str | Path | None = None  # from --web-config
    server: WebServer | None = None
    view_only: bool = True
    configfile: str | Path | None = None  # turnover config file
    defaults: dict[str, Any] | None = None  # CACHEDIR etc. from commandline
    port: int = 8000
    server_options: tuple[str, ...] = ()  # extra commandline arguments after --
    wsgi_app: str = "protein_turnover_website.wsgi"
    page: str | None = None
    mailhost: str | None = None
    sleep: float = 30.0

    def get_server(self) -> WebServer:  # pragma: no cover
        if not has_package("protein_turnover_website"):
            click.secho(
                "Please install protein_turnover_website [pip install protein-turnover-website]!",
                fg="red",
                err=True,
            )
            raise click.Abort()
        server = self.server
        if server is None:  # try for a better server
            s: WebServer
            for s in ["gunicorn", "waitress", "flask"]:  # type: ignore
                if has_package(s):
                    server = s
                    break
        else:
            if not has_package(server):
                click.secho(
                    f"Please install {self.server} [pip install {self.server}]!",
                    fg="red",
                    err=True,
                )
                raise click.Abort()
        assert server is not None
        return server

    def get_webconf(self) -> dict[str, Any]:
        web_config = self.web_config
        if web_config is None:
            if self.configfile is not None and Path(self.configfile).exists():
                web_config = self.configfile
            elif CONFIG.exists():
                web_config = CONFIG

        web_conf = default_conf()

        if web_config:
            # just need JOBSDIR
            click.secho(
                f"reading  web configuration from: {web_config} namespace=website",
                fg="green",
            )
            web_conf.update(
                instance_conf(web_config, ns="website"),
            )
        # from commandline so... last
        if self.defaults is not None:
            web_conf.update(self.defaults)

        if self.mailhost is not None:
            if self.mailhost == "none":
                web_conf["WANT_EMAIL"] = 0  # no point user specifying an email

        # we don't want an email logger for a single use server
        if "LOG_MAIL_SERVER" not in web_conf or self.mailhost == "none":
            web_conf["LOG_MAIL_SERVER"] = "none"
        return web_conf

    def get_website(self, server: WebServer, jobfile: Path) -> Runner:
        return Runner(
            server,
            [
                *APPS[server](self.wsgi_app, self.port),
                *self.server_options,
            ],
            env={"TURNOVER_SETTINGS": str(jobfile)},
            prevent_sig=True,
        )

    def get_mailhost(self) -> str | None:
        return self.mailhost
        # from .config import MAIL_SERVER

        # if self.mailhost is not None:
        #     return self.mailhost
        # return MAIL_SERVER

    def run(self) -> bool:
        """Run full website."""

        server = self.get_server()
        web_conf = self.get_webconf()

        # need to read config file just for jobsdir
        jd = web_conf["JOBSDIR"]
        if isinstance(jd, list):
            jd = jd[0]
        jobsdir = Path(jd).expanduser()
        if not jobsdir.exists():
            jobsdir.mkdir(parents=True, exist_ok=True)
        background = None
        if not self.view_only:
            m = self.get_mailhost()
            email_args = [] if m is None else [f"--mailhost={m}"]
            cfg = [f"--config={self.configfile}"] if self.configfile is not None else []
            background = Runner(
                "background",
                [
                    sys.executable,
                    "-m",
                    "protein_turnover",
                    *cfg,
                    "--level=info",
                    "background",
                    f"--workers={self.workers}",
                    *email_args,
                    str(jobsdir),
                ],
                directory=".",
                prevent_sig=True,
            )
        Url = f"127.0.0.1:{self.port}"
        if self.page is not None:
            Url += f"/{self.page}"

        # ON windows NamedTemporaryFile can't be read
        # by other processes, so we use a directory
        # ... which seems to work... sigh!
        with TemporaryDirectory() as td:
            filename = Path(td) / "turnover-web.toml"
            with filename.open("wb") as fp:
                tomli_w.dump(web_conf, fp)  # type: ignore

            website = self.get_website(server, filename)

            if self.view_only:
                procs = [website]
            else:
                assert background is not None
                procs = [background, website]

            processes = [(p.name, p.start()) for p in procs]

            if self.browse:
                browser(url=f"http://{Url}", sleep=5.0)
            return self.loop(jobsdir, processes)

    def loop(
        self,
        jobsdir: Path,
        processes: list[tuple[str, subprocess.Popen[bytes]]],
    ) -> bool:
        if sys.platform == "win32":
            KILLSIG = signal.CTRL_C_EVENT
        else:
            KILLSIG = signal.SIGINT
        worker = Processing(jobsdir)
        ninterrupts = 0
        prev = datetime.now()
        while True:
            try:
                time.sleep(self.sleep)
                failed = False
                done = 0
                for n, tr in processes:
                    try:
                        retcode = tr.wait(1.0)
                        if retcode != 0:
                            click.echo(f"process failed {n}")
                            failed = True
                        else:
                            done += 1
                    except subprocess.TimeoutExpired:
                        pass
                if failed:
                    raise KeyboardInterrupt()
                if done == len(processes):  # only in testing...
                    return True

            except KeyboardInterrupt:
                # too long between ^C
                now = datetime.now()
                if (
                    ninterrupts > 0
                    and not self.view_only
                    and (now - prev).total_seconds() > 5
                ):
                    ninterrupts = 0
                    prev = now
                    continue
                ninterrupts += 1
                if ninterrupts >= 2 or self.view_only:
                    for name, tr in processes:
                        click.secho(f"terminating... {name}", fg="blue")
                        tr.send_signal(KILLSIG)
                    for name, tr in processes:
                        try:
                            tr.wait(timeout=4.0)
                        except (OSError, subprocess.TimeoutExpired):
                            pass
                    sys.exit(os.EX_OK)

                prev = now

                if not self.view_only and worker.is_processing():
                    click.secho(
                        "Warning! The background process is running a job!",
                        fg="yellow",
                        bold=True,
                    )
                click.secho("interrupt... ^C again to terminate")
        return False


class TestWebRunner(WebRunner):
    @override
    def get_server(self) -> WebServer:
        return "flask"

    @override
    def get_website(self, server: WebServer, jobfile: Path) -> Runner:
        return Runner(
            "test-website",
            [
                sys.executable,
                "-m",
                "protein_turnover.web",  # see "test website below"
                str(jobfile),
            ],
            directory=".",
        )


if __name__ == "__main__":
    # used in testing....
    import click

    @click.command()
    @click.argument("jobfile")
    def testwebsite(jobfile: str):
        """Minimal website"""
        tomlfile = Path(jobfile)
        with tomlfile.open("rb") as fp:
            tomllib.load(fp)

        time.sleep(0.5)  # do some website stuff

    testwebsite()
