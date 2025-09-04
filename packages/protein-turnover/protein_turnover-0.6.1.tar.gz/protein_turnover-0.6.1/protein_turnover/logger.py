from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:
    from typing import Iterator


def hashandlers(logger: logging.Logger) -> bool:
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return bool(logger.handlers)
    return logger.hasHandlers()  # pragma: no cover


Result = TypeVar("Result")

logger = logging.getLogger("protein_turnover")


def init_logger(
    *,
    level: str | int = logging.INFO,
    logfile: Path | str | None = None,
    reinit: bool = False,
) -> None:
    from .config import LOG_FORMAT

    h: logging.Handler

    if isinstance(level, str):
        level = level.upper()

    def add_handler(h: logging.Handler) -> None:  # pragma: no cover
        fmt = logging.Formatter(LOG_FORMAT)
        h.setFormatter(fmt)
        logger.addHandler(h)

    logger.setLevel(level)
    if reinit:
        for h in list(logger.handlers):  # pragma: no cover
            logger.removeHandler(h)

    if not hashandlers(logger):
        if logfile is None or logfile == "-":
            add_handler(logging.StreamHandler())
        else:
            lf = Path(logfile)
            if not lf.parent.exists():
                lf.parent.mkdir(parents=True, exist_ok=True)
            add_handler(logging.FileHandler(str(logfile), mode="w"))


def log_iterator(
    it: Iterator[Result],
    *,
    total: int,
    desc: str,
    level: int = 1,
    number_of_bg_processes: int = 1,
    num_logs: int = 100,
) -> Iterator[Result]:
    n = max(1, total // num_logs)
    if number_of_bg_processes == 1:
        fmt = f"{desc}: [%d/%d %d%%]"
    else:
        fmt = f"{desc}[{level}/{number_of_bg_processes}]: [%d/%d %d%%]"

    for idx, i in enumerate(it, start=1):
        yield i
        if (idx % n) == 0:
            pct = int(idx * 100 / total)
            logger.info(fmt, idx, total, pct)
    logger.info(fmt, total, total, 100)


@contextmanager
def show_log():
    oldlevel = logger.getEffectiveLevel()
    h = None
    if not hashandlers(logger):  # local handler
        h = logging.StreamHandler()
        logger.addHandler(h)
    try:
        logger.setLevel(logging.INFO)
        yield
    finally:
        logger.setLevel(oldlevel)
        if h is not None:
            logger.removeHandler(h)


@contextmanager
def show_fit_warnings(quiet: bool = False):
    from . import fitenvelopes

    old = fitenvelopes.LOG_ERRORS
    oldlevel = None
    h = None
    if not quiet:
        fitenvelopes.LOG_ERRORS = True
        if not logger.isEnabledFor(logging.WARNING):  # pragma: no cover
            oldlevel = logger.getEffectiveLevel()
            logger.setLevel(logging.WARNING)
        if not logger.hasHandlers():  # pragma: no cover
            h = logging.StreamHandler()
            logger.addHandler(h)
    try:
        yield
    finally:
        if not quiet:
            fitenvelopes.LOG_ERRORS = old
            if oldlevel is not None:  # pragma: no cover
                logger.setLevel(oldlevel)
            if h is not None:  # pragma: no cover
                logger.removeHandler(h)
