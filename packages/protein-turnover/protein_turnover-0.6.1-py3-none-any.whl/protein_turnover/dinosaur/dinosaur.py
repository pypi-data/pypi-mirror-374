from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..logger import logger
from ..resourcefiles import MzMLResourceFile
from ..utils import IO
from .cmd import Command


@dataclass
class DinoRunner:
    jarpath: Path
    javapath: Path = Path("java")

    def cmdline(self) -> list[str]:
        from shutil import which

        javapath = which(self.javapath or "java")
        if javapath is None:
            return []

        return [str(javapath), "-jar", str(self.jarpath.absolute())]

    @classmethod
    def from_config(cls) -> DinoRunner | None:
        from ..config import DINOSAUR_JAR, JAVA_PATH

        if not DINOSAUR_JAR:
            return None
        if JAVA_PATH is None:
            return None
        return DinoRunner(jarpath=Path(DINOSAUR_JAR), javapath=Path(JAVA_PATH))

    def can_run(self) -> bool:
        from shutil import which

        return self.jarpath.exists() and which(self.javapath) is not None

    def run(self, mzml: MzMLResourceFile) -> None | int:
        cmdline = self.cmdline() + [
            "--verbose",
            f"--outDir={mzml.cache_dir or '.'}",
            f"--outName={mzml.hash}",
            str(mzml.original.absolute()),
        ]

        cmd = Command(cmdline)

        for line in cmd.output:
            logger.info("dinosaur: %s", line)
        if cmd.returncode:
            logger.error("failed to generate dinosaur for %s", mzml.original.name)
            return cmd.returncode

        output = mzml.cache_dir / f"{mzml.hash}.features.tsv"

        df = pd.read_csv(output, sep="\t")
        output.unlink()
        output = mzml.cache_dinosaur()
        logger.info("writing dinosaur: %s", output)
        IO(output, df).save_df()
        return cmd.returncode


def mzml_dinosaur(mzml: MzMLResourceFile) -> None:
    dino = DinoRunner.from_config()
    if dino is None or not dino.can_run():
        return

    dino.run(mzml)
