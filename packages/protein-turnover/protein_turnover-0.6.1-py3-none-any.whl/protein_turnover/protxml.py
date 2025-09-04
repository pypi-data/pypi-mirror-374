from __future__ import annotations

import logging
import mmap
import re
from pathlib import Path
from typing import Iterator
from typing import Literal

import pandas as pd

from .logger import logger
from .resourcefiles import ProtXMLResourceFile
from .utils import human
from .utils import IO

# CALL TREE
#
# getprotxml
#    | --- protxml_create (if no cache)
#               |  --- protxml_raw
#               |  --- protxml_out
#                          | -- IO.write_df
#    | IO.read_df

PROTEIN = re.compile(b"<protein ")

PROT_OR_PEP = re.compile(
    b'(?P<key>protein_name|unique_stripped_peptides)="(?P<value>[^"]+)"',
)
PROTEIN_NAME = re.compile(b'<protein\\s+protein_name="([^"]+)"')


## @export
def scan_proteins(protxml: Path) -> Iterator[int]:
    """Very fast inspection of prot.xml spectra queries"""
    with protxml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for m in PROTEIN.finditer(mm):
                yield m.start(0)


def scan_proteins_names(protxml: Path) -> Iterator[str]:
    """Very fast inspection of prot.xml spectra queries"""
    with protxml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for m in PROTEIN_NAME.finditer(mm):
                yield m.group(1).decode("ascii")


def full_scan_proteins(  # pragma: no cover
    protxml: Path,
) -> Iterator[
    tuple[Literal["protein_name"], str] | tuple[Literal["peptides"], list[str]]
]:
    """Very fast inspection of prot.xml spectra queries"""
    with protxml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for m in PROT_OR_PEP.finditer(mm):
                key, value = m.group("key", "value")
                if key == b"protein_name":
                    yield "protein_name", value.decode("ascii")
                else:
                    yield "peptides", value.decode("ascii").split("+")


def full_scan_proteins2(  # pragma: no cover
    protxml: Path,
) -> Iterator[tuple[str, list[str]]]:
    """Very fast inspection of prot.xml spectra queries"""
    ckey: str | None = None
    for key, value in full_scan_proteins(protxml):
        if key == "peptides":
            assert ckey is not None
            yield ckey, value  # type: ignore
        else:
            ckey = value  # type: ignore


def protxml_raw(
    protxml: Path,
    level: int = 0,
    number_of_bg_processes: int = 1,
) -> pd.DataFrame:
    from .broken_api import ProtXmlDataFrame

    logger.info("reading: %s", protxml.name)
    df = ProtXmlDataFrame(
        protxml,
        level=level,
        number_of_bg_processes=number_of_bg_processes,
    )
    logger.info("done: %s", protxml.name)
    return df


def getprotxml(protxml: ProtXMLResourceFile) -> pd.DataFrame:
    if protxml.cache_protxml_ok():
        data = protxml.cache_protxml()
        logger.info('getprotxml: reading: "%s"', data.name)
        df = IO(data).read_df()
        logger.info('getprotxml: finished reading: "%s" [%d]', data.name, len(df))

    else:
        if not protxml.exists():
            raise FileNotFoundError(f"can't find file: {protxml.original}")
        logger.info('getprotxml: creating cache "%s"', protxml.original.name)
        protxml_create(protxml)
        assert protxml.cache_protxml_ok()
        df = IO(protxml.cache_protxml()).read_df()

    return df


def protxml_out(
    df: pd.DataFrame,
    protxml: ProtXMLResourceFile,
) -> None:
    """Write cached version of protxml dataframe"""
    from .utils import IO

    protxmldf = protxml.cache_protxml()

    logger.info("writing file: %s: total=%s", protxmldf.name, len(df))

    # df = dehydrate_protxml(df)
    IO(protxmldf, df).save_df()

    if logger.isEnabledFor(logging.INFO):  # pragma: no cover
        mem = df.memory_usage(deep=True)
        size = protxmldf.stat().st_size
        osize = protxml.original.stat().st_size

        logger.info(
            "memory=%s disk=%s original=%s",
            human(mem.sum()),
            human(size),
            human(osize),
        )


def protxml_create(
    protxml: ProtXMLResourceFile,
    level: int = 0,
    number_of_bg_processes: int = 1,
) -> int:
    df = protxml_raw(
        protxml.original,
        level=level,
        number_of_bg_processes=number_of_bg_processes,
    )
    protxml_out(df, protxml)
    return level


# def dehydrate_protxml(df: pd.DataFrame) -> pd.DataFrame:
#     return df
