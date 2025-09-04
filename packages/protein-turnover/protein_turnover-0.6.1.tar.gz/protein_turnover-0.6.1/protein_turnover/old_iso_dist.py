from __future__ import annotations

from typing import Callable

import numpy as np
from scipy.fft import fft
from scipy.fft import ifft

from .utils import ATOMICPROPERTIES
from .utils import NAMES
from .utils import PeptideInfo
from .utils import PeptideSettings


def isotopic_distribution(
    pepinfo: PeptideInfo,
    abundance: float | None = None,
    abundanceCutoff: float = 1e-10,
    maxMass: int = 100,
    Ralg: bool = True,
) -> np.ndarray:
    # pragma: no cover
    """return abundance of "heavy" peptides"""
    if abundance is None:
        ab = pepinfo.naturalAtomicAbundances
    else:
        ab = pepinfo.labelledAtomicAbundances(abundance)

    abundances = {pepinfo.settings.labelledElement: ab}

    formula = pepinfo.formula

    maxElements = np.sum(formula > 0, dtype=int)

    A = np.zeros((maxElements, maxMass), np.complex64 if Ralg else np.float64)

    elements = []
    for i, e in enumerate(NAMES):
        n = formula[i]
        if n > 0:
            elements.append(n)
            if e in abundances:
                a = abundances[e]
            else:
                # use natural abundance
                a = ATOMICPROPERTIES[e]["abundance"]
            A[len(elements) - 1, 0 : len(a)] = a

            if Ralg:
                A[len(elements) - 1, :] = fft(A[len(elements) - 1, :], maxMass)[
                    :maxMass
                ]

    tA = A if Ralg else fft(A)

    ptA = np.ones((maxMass,), dtype=np.complex128)

    for i in range(maxElements):
        ptA *= tA[i] ** elements[i]

    riptA = np.real(ifft(ptA))  # type: ignore
    mx = np.max(np.where(riptA > abundanceCutoff))
    riptA = riptA[0 : int(mx) + 1]
    return np.fmax(riptA, 0.0)
    # return np.where(riptA > 0.0, riptA, 0.0)


def mk_maxIso(settings: PeptideSettings) -> Callable[[str], int]:
    # pragma: no cover
    from .config import ABUNDANCE_CUTOFF

    def maxIso(peptide: str) -> int:
        pepinfo = PeptideInfo(peptide, settings)
        r = isotopic_distribution(
            pepinfo,
            settings.maximumLabelEnrichment,
            abundanceCutoff=ABUNDANCE_CUTOFF,
        )
        return len(r) - 1

    return maxIso
