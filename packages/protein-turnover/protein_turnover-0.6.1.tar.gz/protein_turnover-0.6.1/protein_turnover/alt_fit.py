from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.fft import irfft
from scipy.fft import irfftn
from scipy.fft import next_fast_len
from scipy.fft import rfft
from scipy.fft import rfftn

from .utils import ensure_pos
from .utils import PeptideInfo
from .utils import resize

if TYPE_CHECKING:
    from typing import Callable
    from .utils import PeptideSettings


def nextfast(natoms: int) -> int:
    return next_fast_len(natoms + 1, real=True)  # type: ignore


# see https://pubs.acs.org/doi/pdf/10.1021/ac500108n
def fractions1D(abundances: np.ndarray, natoms: int) -> np.ndarray:
    nlen = nextfast(natoms)
    c = np.zeros(nlen, np.float64)
    c[:2] = abundances
    return irfft(
        rfft(c, overwrite_x=True) ** natoms,  # type: ignore
        nlen,
        overwrite_x=True,
    )[: natoms + 1]  # type: ignore


def fractionsND(abundances: np.ndarray, natoms: int) -> np.ndarray:
    nlen = nextfast(natoms)
    shape = tuple([nlen] * (len(abundances) - 1))
    m = len(shape)
    c = np.zeros(shape, np.float64)

    z = lambda: [0] * m
    # abundance zero is the main stable isotope
    c[tuple(z())] = abundances[0]

    for i, a in enumerate(abundances[1:]):
        idx = z()
        idx[i] = 1
        c[tuple(idx)] = a

    return irfftn(rfftn(c, overwrite_x=True) ** natoms, c.shape, overwrite_x=True)  # type: ignore


def fractions(abundances: np.ndarray, iabundance: int, natoms: int) -> np.ndarray:
    if len(abundances) == 2:
        return fractions1D(abundances, natoms)
    r = fractionsND(abundances, natoms)
    # pull out iabundance axis
    idx = [0] * r.ndim
    idx[iabundance - 1] = slice(natoms + 1)  # type: ignore
    return r[tuple(idx)]


def isotopic_distribution(
    pepinfo: PeptideInfo,
    abundance: float | None = None,
) -> np.ndarray:
    """implements paper https://pubs.acs.org/doi/pdf/10.1021/ac500108n"""
    # also https://dx.doi.org/10.1021/ac500108n

    if abundance is None:
        abundances = pepinfo.naturalAtomicAbundances
    else:
        abundances = pepinfo.labelledAtomicAbundances(abundance)

    r = fractions(abundances, pepinfo.iabundance, pepinfo.elementCount)
    return np.fmax(r, 0.0)


def mk_maxIso(settings: PeptideSettings) -> Callable[[str], np.int32]:
    from .config import ABUNDANCE_CUTOFF

    abundances = settings.labelledAtomicAbundancesAtMaxEnrich
    iabundance = settings.iabundance

    def maxIso(peptide: str) -> np.int32:
        n = settings.getElementCountFromPeptide(peptide)
        r = fractions(abundances, iabundance, n)
        mx = np.max(np.where(r > ABUNDANCE_CUTOFF))
        return np.int32(mx + 1)

    return maxIso


def make_envelope_array(
    pepinfo: PeptideInfo,
    maxIso: int,
) -> tuple[np.ndarray, np.ndarray]:
    enrichments = pepinfo.getEnrichments(maxIso)

    isotope_envelope_basis = np.zeros(
        shape=(maxIso + 1, len(enrichments)),
        dtype=np.float64,
    )
    for i, element_enrichment_level in enumerate(enrichments):
        d = isotopic_distribution(pepinfo, element_enrichment_level)
        max_el = min(len(d), maxIso + 1)
        isotope_envelope_basis[:max_el, i] = d[:max_el]
    return enrichments, isotope_envelope_basis


def heavy_dist(
    pepinfo: PeptideInfo,
    isotopeEnvelopesMinus: np.ndarray,  # without -1 isoDiff
) -> np.ndarray:
    """isotopeEnvelope - natural abundance"""
    naturalIsotopeEnvelope = natural_dist(pepinfo, isotopeEnvelopesMinus[0])
    naturalIsotopeEnvelope = resize(naturalIsotopeEnvelope, len(isotopeEnvelopesMinus))

    return ensure_pos(
        isotopeEnvelopesMinus - naturalIsotopeEnvelope,
    ).astype(np.float32)


def natural_dist(
    pepinfo: PeptideInfo,
    monoScale: float,
) -> np.ndarray:
    isod = isotopic_distribution(pepinfo)
    denom = isod[0]
    denom = denom if denom > 0.0 else 1.0
    return monoScale * isod / denom


# from .old_iso_dist import isotopic_distribution, mk_maxIso # type: ignore
