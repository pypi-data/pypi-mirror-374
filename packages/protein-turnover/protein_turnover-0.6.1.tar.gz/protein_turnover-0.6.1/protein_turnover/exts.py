from __future__ import annotations

from sys import byteorder

# change this to cache bust
VERSION = 1

EXT = "parquet"
PEPXML = f".pep-v{VERSION}.{EXT}"
PROTXML = f".prot-v{VERSION}.{EXT}"
MZMAP = f".{byteorder}-v{VERSION}.mzi"
DINOSAUR = f".features-v{VERSION}.{EXT}"
MZML = f".mzml-v{VERSION}.{EXT}"
EICS = f".eics-v{VERSION}.{EXT}"
## @export
RESULT_EXT = ".sqlite"  # {EXT}"  # f".v{VERSION}.{EXT}"
