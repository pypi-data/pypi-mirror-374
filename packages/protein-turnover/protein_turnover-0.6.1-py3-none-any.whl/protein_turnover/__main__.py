from __future__ import annotations

from . import background_ui
from . import pymz_ui
from . import web_ui
from .cli import cli
from .sqla import iso_peaks_ui

__all__ = ["background_ui", "pymz_ui", "iso_peaks_ui", "web_ui", "cli"]

# pylint: disable=unused-import


# REM: imports should *not* import scipy,pandas,numpy!!!! Just click and .cli
# and a few system modules os, sys, typing... BE CAREFUL! otherwise load
# times might slow user interaction.

if __name__ == "__main__":  # pragma: no cover
    cli.main(prog_name="turnover")
