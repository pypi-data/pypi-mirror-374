from __future__ import annotations

import hashlib
from abc import ABC
from abc import abstractmethod
from pathlib import Path

from typing_extensions import override

from .exts import DINOSAUR
from .exts import EICS
from .exts import EXT
from .exts import MZMAP
from .exts import MZML
from .exts import PEPXML
from .exts import PROTXML
from .exts import RESULT_EXT


def hash256(filename: Path, bufsize: int = 4096 * 8, algo: str = "sha256") -> str:
    sha256_hash = hashlib.new(algo, usedforsecurity=False)
    with filename.open("rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(bufsize), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def fileok(cached: list[Path], original: Path) -> bool:
    if not cached:  # pragma: no cover
        return False
    if not original.is_file():
        return False
    omtime = original.stat().st_mtime
    for cache in cached:
        if not cache.is_file() or omtime > cache.stat().st_mtime:
            return False
    return True


class BaseResourceFile(ABC):
    def __init__(
        self,
        original: Path | str,
        cache_dir: Path | str | None = None,
    ):
        self.original = Path(original).expanduser().resolve()
        if cache_dir is None:
            self.cache_dir = self.original.parent
        else:
            self.cache_dir = Path(cache_dir).expanduser().resolve()
        self._hash: str | None = None

    @property
    def name(self) -> str:
        return self.original.name

    def exists(self) -> bool:
        return self.original.exists()

    def extok_(self, *ext: str) -> bool:
        targets = [self.cache_file_(e) for e in ext]
        return fileok(targets, self.original)

    def cache_file_(self, ext: str) -> Path:
        return self.cache_dir.joinpath(self.hash + ext)

    def cache_ok(self) -> bool:
        ok = self.all_cache_files()
        return fileok(ok, self.original)

    def ensure_cache_dir(self):
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def hash(self) -> str:
        if self._hash is not None:
            return self._hash

        self._hash = self.get_hash_()
        return self._hash

    def get_hash_(self) -> str:
        return hash256(self.original)

    def cleanup(self) -> None:
        for pth in self.all_cache_files():
            try:
                pth.unlink(missing_ok=True)
            except OSError:  # pragma: no cover
                pass

    @abstractmethod
    def all_cache_files(self) -> list[Path]:  # pragma: no cover
        return []

    def get_lock_files_(self) -> list[Path]:
        return [path.parent / (path.name + ".lock") for path in self.all_cache_files()]

    def lock(self) -> None:
        """Don't delete a cache file "X" if it has an "X.lock" file"""
        for path in self.get_lock_files_():
            path.touch()

    def unlock(self) -> None:
        for path in self.get_lock_files_():
            try:
                path.unlink(missing_ok=True)
            except OSError:  # pragma: no cover
                pass

    def is_locked(self) -> bool:
        for path in self.get_lock_files_():
            if path.exists():
                return True
        return False


class MzMLResourceFile(BaseResourceFile):
    @property
    def runName(self) -> str:
        """Name possibly in pep.xml file as <spectrum_query spectrum="{runName}.{start_scan}.{end_scan}.0 ...>"""
        return self.original.stem

    def cache_mzml(self) -> Path:
        return self.cache_file_(MZML)

    def cache_memmap(self) -> Path:
        return self.cache_file_(MZMAP)

    def cache_dinosaur(self) -> Path:  # pragma: no cover
        return self.cache_file_(DINOSAUR)

    def cache_mzml_ok(self) -> bool:
        return self.extok_(MZML)

    def cache_memmap_ok(self) -> bool:
        return self.extok_(MZMAP)

    # def cache_dinosaur_ok(self):
    #     from .dinosaur.dinosaur import DinoRunner

    #     ok = self.extok_(DINOSAUR)
    #     if ok:
    #         return True

    #     dino = DinoRunner.from_config()
    #     # no dino file check if we can generate it...
    #     if dino is not None and dino.can_run():
    #         return False
    #     # ok we can't generate it so cache is "fine..."
    #     return True

    @override
    def all_cache_files(self) -> list[Path]:
        return [self.cache_mzml(), self.cache_memmap()]

    # @override
    # def cache_ok(self) -> bool:
    #     ok = super().cache_ok()
    #     if not ok:
    #         return ok
    #     return self.cache_dinosaur_ok()


class MzMLResourceFileLocal(MzMLResourceFile):
    def __init__(
        self,
        original: Path | str,
        cache_dir: Path | str | None = None,
        *,
        name: str | Path | None = None,
        ext: str = EXT,
    ):
        super().__init__(original, cache_dir)
        if name is None:
            name = self.name
        self.outname = Path(name)
        if not ext.startswith("."):
            ext = "." + ext
        self.ext = ext

    @override
    def cache_file_(self, ext: str) -> Path:
        return self.cache_dir.joinpath(self.outname.with_suffix(ext))

    @override
    def cache_mzml(self) -> Path:
        return self.cache_file_(self.ext)

    @override
    def cache_memmap(self) -> Path:
        return self.cache_file_(".mzi")

    @override
    def cache_mzml_ok(self) -> bool:
        return self.extok_(self.ext)

    @override
    def cache_memmap_ok(self) -> bool:
        return self.extok_(".mzi")


class PepXMLResourceFile(BaseResourceFile):
    def cache_pepxml(self) -> Path:
        return self.cache_file_(PEPXML)

    def cache_pepxml_ok(self) -> bool:
        return self.extok_(PEPXML)

    @override
    def all_cache_files(self) -> list[Path]:
        return [self.cache_pepxml()]


class PepXMLResourceFileLocal(PepXMLResourceFile):
    def __init__(
        self,
        original: Path | str,
        cache_dir: Path | str | None = None,
        *,
        name: str | Path | None = None,
        ext: str = EXT,
    ):
        super().__init__(original, cache_dir)
        if name is None:
            name = self.name
        self.outname = Path(name)
        if not ext.startswith("."):
            ext = "." + ext
        self.ext = ext

    @override
    def cache_file_(self, ext: str) -> Path:
        return self.cache_dir.joinpath(self.outname.with_suffix(ext))

    @override
    def cache_pepxml(self) -> Path:
        return self.cache_file_(self.ext)

    @override
    def cache_pepxml_ok(self) -> bool:
        return self.extok_(self.ext)


class ProtXMLResourceFile(BaseResourceFile):
    def cache_protxml(self) -> Path:
        return self.cache_file_(PROTXML)

    def cache_protxml_ok(self) -> bool:
        return self.extok_(PROTXML)

    @override
    def all_cache_files(self) -> list[Path]:
        return [self.cache_protxml()]


class ProtXMLResourceFileLocal(ProtXMLResourceFile):
    def __init__(
        self,
        original: Path | str,
        cache_dir: Path | str | None = None,
        *,
        name: str | Path | None = None,
        ext: str = EXT,
    ):
        super().__init__(original, cache_dir)
        if name is None:
            name = self.name
        self.outname = Path(name)
        if not ext.startswith("."):
            ext = "." + ext
        self.ext = ext

    @override
    def cache_protxml(self) -> Path:
        return self.cache_file_(self.ext)

    @override
    def cache_protxml_ok(self) -> bool:
        return self.extok_(self.ext)

    @override
    def cache_file_(self, ext: str) -> Path:
        return self.cache_dir.joinpath(self.outname.with_suffix(ext))


class ResultsResourceFile(BaseResourceFile):
    def cache_result(self) -> Path:
        return self.cache_file_(RESULT_EXT)

    def cache_pepxml(self) -> Path:
        return self.cache_file_(PEPXML)

    def cache_envelope(self) -> Path:
        return self.cache_file_(EICS)

    def cache_partial_envelope(self, idx: int) -> Path:
        return self.cache_file_(f"-{idx}{EICS}")

    def has_result(self) -> bool:
        return self.cache_result().exists()

    @override
    def cache_file_(self, ext: str) -> Path:
        return self.cache_dir.joinpath(self.original.name + ext)

    @override
    def all_cache_files(self) -> list[Path]:
        return [self.cache_result(), self.cache_pepxml(), self.cache_envelope()]


class ResourceFiles:
    def __init__(
        self,
        pepxmls: list[PepXMLResourceFile],
        protxml: ProtXMLResourceFile,
        mzmlfiles: list[MzMLResourceFile],
    ):
        self.pepxmls = pepxmls
        self.protxml = protxml
        self.mzmlfiles = mzmlfiles
        self.cache_dirs = {
            *[s.cache_dir for s in pepxmls],
            *[s.cache_dir for s in mzmlfiles],
        }

    def all_cache_files_(self) -> list[BaseResourceFile]:
        ret = [s for s in [*self.pepxmls, *self.mzmlfiles] if s.exists()]
        if self.protxml.exists():
            ret.append(self.protxml)
        return ret

    def lock(self) -> None:
        for resourcefile in self.all_cache_files_():
            resourcefile.lock()

    def unlock(self) -> None:
        for resourcefile in self.all_cache_files_():
            resourcefile.unlock()

    def is_locked(self) -> bool:
        for resourcefile in self.all_cache_files_():
            if resourcefile.is_locked():
                return True
        return False

    def todo(self) -> list[BaseResourceFile]:
        ret: list[BaseResourceFile] = []
        for pepxml in self.pepxmls:
            if pepxml.exists() and not pepxml.cache_pepxml_ok():
                ret.append(pepxml)
        for mzml in self.mzmlfiles:
            if mzml.exists() and not mzml.cache_mzml_ok():
                ret.append(mzml)
        if self.protxml.exists() and not self.protxml.cache_ok():
            ret.append(self.protxml)

        return ret

    def ensure_directories(self) -> None:
        for cd in self.cache_dirs:
            if not cd.is_dir():  # pragma: no cover
                cd.mkdir(parents=True, exist_ok=True)
