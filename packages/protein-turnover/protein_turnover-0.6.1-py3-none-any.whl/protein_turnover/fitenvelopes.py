from __future__ import annotations

import warnings
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from math import fabs
from typing import NamedTuple
from typing import TYPE_CHECKING
from typing import TypeVar

import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.linalg import LinAlgError
from scipy.linalg import lstsq
from scipy.linalg import norm
from scipy.optimize import curve_fit
from scipy.optimize import nnls
from scipy.special import erf  # pylint: disable=no-name-in-module
from scipy.stats import pearsonr

from .alt_fit import heavy_dist
from .alt_fit import make_envelope_array
from .logger import logger
from .utils import ensure_pos
from .utils import PeptideInfo
from .utils import resize

if TYPE_CHECKING:
    from typing import Callable
    from typing import Iterator
    from .utils import PeptideSettings

FAIL_E_CURVE = 0
FAIL_W_CURVE = 1
FAIL_W_QUAD = 2
FAIL_W_H_CURVE = 3
FAIL_E_H_CURVE = 4
FAIL_W_PEARSON = 5
FAIL_E_BOUNDARY = 6
FAIL_E_EICS = 7
FAIL_W_PEARSON2 = 8
FAIL_E_NOEICS = 9

FAILS = {
    FAIL_E_CURVE: "envelope curve_fit error",
    FAIL_W_CURVE: "envelope curve_fit warning",
    FAIL_W_QUAD: "envelope quadrature warning",
    FAIL_W_H_CURVE: "heavy curve_fit warning",
    FAIL_E_H_CURVE: "heavy curve_fit error",
    FAIL_W_PEARSON: "pearson correlation warning for heavy vs theortical dist",
    FAIL_E_BOUNDARY: "no intensities within boundary",
    FAIL_E_EICS: "can't fit EICS",
    FAIL_W_PEARSON2: "pearson correlation warning for isotope vs theortical dist",
    FAIL_E_NOEICS: "no EICS found",
}

LOG_ERRORS = False  # see show_fit_warnings in logger.py

Result = TypeVar("Result")

R2: float = np.sqrt(2.0).astype(np.float64)
RPI2: float = np.sqrt(np.pi / 2.0).astype(np.float64)
NSIGMA = 2.0
DELTA_ERF: float = (RPI2 * (erf(NSIGMA / R2) - erf(-NSIGMA / R2))).astype(np.float64)
USE_QUAD = False
QUAD_LIMIT = 500


def fails(ival: int) -> str:
    return ", ".join(s for i, s in FAILS.items() if ival & (1 << i))


@dataclass
class IsotopeEnvelope:
    adjustedRsq: np.ndarray
    isotopeEnvelopes: np.ndarray  # 1-D
    monoFitParams: np.ndarray  # 1-D  [mu, sigma, scale, baseline]
    inv_ratio: float
    monoPeakArea: float
    maxPeakArea: float
    sigma: float
    avg_rsq: float


@dataclass
class LabelledEnvelope:
    labelledEnvelopes: np.ndarray  # 1-D
    theoreticalDist: np.ndarray
    relativeIsotopeAbundance: float
    enrichment: float
    # labelEnrichment2: float
    heavyCor: float
    heavyCor2: float
    nnls_residual: float
    totalNNLSWeight: float
    totalIntensityWeight: float


@dataclass
class Envelope(IsotopeEnvelope, LabelledEnvelope):
    @classmethod
    def make_all(
        cls,
        env: IsotopeEnvelope,
        # heavy: HeavyEnvelope,
        labelled: LabelledEnvelope,
    ) -> Envelope:
        args = {**asdict(env), **asdict(labelled)}
        return cls(**args)  # type: ignore


class RSquared(NamedTuple):
    r_squared: float
    adj_r_squared: float


def normalIntensityFunction(
    rt: float | np.ndarray,
    mu: float,
    sigma: float,
    scale: float,
    baseline: float,
) -> float | np.ndarray:
    return scale * np.exp(-0.5 * (rt - mu) ** 2 / sigma**2) + baseline


def lm_adjust(
    mat: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    df: int,
) -> RSquared:
    dx = mat @ x - y
    return adjust(dx, y, df)


# def curve_adjust(
#     func: Callable[[float | np.ndarray, float, float, float], float | np.ndarray],
#     popt: np.ndarray,
#     x: np.ndarray,
#     y: np.ndarray,
#     df: int,
# ) -> RSquared:
#     dx = func(x, *popt) - y
#     return adjust(dx, y, df)


# https://en.wikipedia.org/wiki/Coefficient_of_determination
def adjust(dx: np.ndarray, y: np.ndarray, df: int) -> RSquared:
    rss = np.sum(dx**2)
    ymean = np.mean(y)
    tss = np.sum((y - ymean) ** 2)
    if tss > 0.0:
        r_squared = 1.0 - rss / tss
        n = len(y)
        if n > df:
            adj_r_squared = 1.0 - ((n - 1) / (n - df)) * (1.0 - r_squared)
        else:
            adj_r_squared = r_squared
    else:
        r_squared, adj_r_squared = np.nan, np.nan
    return RSquared(r_squared, adj_r_squared)


def catch_warnings(
    func: Callable[[], Result],
    peptide: str,
    msg: str,
) -> tuple[Result, int]:  # Literal[0,1]
    with warnings.catch_warnings(record=True) as warn:
        warnings.simplefilter("always")
        ret = func()
    if warn and LOG_ERRORS:
        for w in warn:
            message = str(w.message)
            if "\n" in message:
                message, _ = message.split("\n", 1)

            logger.warning(msg, peptide, message)
    return ret, 1 if warn else 0


def fitIntensities(
    mono_intensity: np.ndarray,  # float[N,2 or 1]
    intensities: np.ndarray,  # float[:,N]
) -> Iterator[list[float]]:
    with_origin = mono_intensity.shape[1] == 2
    for intensity in intensities:
        try:
            _res = lstsq(mono_intensity, intensity)
            assert _res is not None
            x, _residues, rank, _s = _res
            if with_origin:
                alpha, slope = x
            else:
                alpha, slope = 0.0, x[0]

            r = lm_adjust(mono_intensity, x, intensity, df=rank)
            adj_r_squared = r.adj_r_squared
        except LinAlgError as e:
            if LOG_ERRORS:
                logger.error("fitIntensities: %s", e)
            adj_r_squared, slope, alpha = np.nan, np.nan, np.nan
        yield [adj_r_squared, slope, alpha]


@dataclass
class MonoFit:
    area: float
    lBoundary: float
    rBoundary: float
    fail: int = 0
    popt: np.ndarray = field(default_factory=lambda: np.zeros(4))
    pcov: np.ndarray = field(default_factory=lambda: np.zeros(16).reshape((4, 4)))

    @property
    def sigma(self) -> float:
        return float(np.average(np.sqrt(np.diag(self.pcov))))


def interpolateRT(
    rt: np.ndarray,
    intensity: np.ndarray,
    step: float = 0.5,
    *,
    rolling: int = 5,
) -> pd.DataFrame:
    n = len(rt)
    rtmin, rtmax = rt.min(), rt.max()
    if n > 0:
        s = (rtmax - rtmin) / n
        s = min(step, s)
    else:
        s = step
    interpolated_rt = np.arange(rtmin, rtmax + 1e-4, step=s)
    interpolated = lambda rtv: np.interp(rtv, rt, intensity)
    interpolated_i = interpolated(interpolated_rt)
    monoData = pd.DataFrame(dict(rt=interpolated_rt, int=interpolated_i))
    if rolling > 0:
        monoData["int"] = (
            monoData["int"].rolling(rolling, min_periods=1, center=True).mean()
        )

    return monoData


def fitMonoEnvelope(
    rt: np.ndarray,
    intensity: np.ndarray,
    interpolate: bool = True,
    use_quadrature: bool = False,
    peptide: str = "unk peptide",
) -> MonoFit:
    if interpolate:
        monoData = interpolateRT(rt, intensity)
    else:
        monoData = pd.DataFrame(dict(rt=rt, int=intensity))

    monoData = monoData.dropna(axis="index")
    if len(monoData) == 0:
        return MonoFit(0.0, 0.0, 0.0, 1 << FAIL_E_CURVE)

    i = monoData["int"].argmax()
    pos = monoData.iloc[i]

    # returns a smaller sigma than R
    def fit() -> tuple[np.ndarray, np.ndarray]:
        popt, pcov, *_ = curve_fit(
            normalIntensityFunction,
            monoData["rt"].to_numpy(),
            monoData["int"].to_numpy(),
            p0=(max(pos["rt"], 0.0), 1.0, max(pos["int"], 1e-5), 0.0),
            # method="lm"
            # maxfev=100,
            # mu,sigma, scale, baseline
            bounds=(
                np.array([0.0, 1e-6, 1e-6, 0.0]),
                np.array([np.inf, np.inf, np.inf, np.inf]),
            ),
        )
        return popt, pcov

    try:
        (popt, pcov), fail = catch_warnings(
            fit,
            peptide,
            "fitMonoEnvelope::curve_fit[%s]: %s",
        )
        fail = fail << FAIL_W_CURVE

    except (RuntimeError, TypeError) as e:
        if LOG_ERRORS:
            logger.error("fitMonoEnvelope::curve_fit[%s]: %s", peptide, e)
        return MonoFit(0.0, 0.0, 0.0, 1 << FAIL_E_CURVE)
    popt[1] = fabs(popt[1])  # ensure sigma is positive

    mu, sigma, kscale, base = popt

    lBoundary: float = max(mu - NSIGMA * sigma, rt[0])
    rBoundary: float = min(mu + NSIGMA * sigma, rt[-1])

    eicIds = (rt >= lBoundary) & (rt <= rBoundary)

    if eicIds.sum() == 0:
        return MonoFit(0.0, lBoundary, rBoundary, fail | 1 << FAIL_E_BOUNDARY, popt)

    if use_quadrature:

        def integrate() -> float:
            monoPeakArea, _ = quad(
                lambda rtv: np.interp(rtv, rt, intensity),
                lBoundary,
                rBoundary,
                limit=QUAD_LIMIT,
                # epsabs=1e-6,
                epsrel=1e-6,
            )
            return monoPeakArea

        monoPeakArea, fail2 = catch_warnings(
            integrate,
            peptide,
            "fitIsotopeEnvelopes::quad[%s]: %s",
        )
        fail |= fail2 << FAIL_W_QUAD

    else:
        monoPeakArea = base * (rBoundary - lBoundary) + kscale * sigma * RPI2 * (
            erf((rBoundary - mu) / sigma / R2) - erf((lBoundary - mu) / sigma / R2)
        )
    return MonoFit(
        monoPeakArea,
        lBoundary,
        rBoundary,
        fail,
        popt,
        pcov,
    )


def fitAllIntensities(im: np.ndarray, intensities: np.ndarray) -> np.ndarray:
    isotopeRegressions = np.array(
        list(fitIntensities(im, intensities)),
        dtype=np.float32,
    )
    return isotopeRegressions


def fitIsotopeEnvelopes(
    rawEIC: np.ndarray,  # [maxIso+2,len(rt),2]
    peptide: str = "unk peptide",
) -> tuple[IsotopeEnvelope | None, int]:
    from .config import WITH_ORIGIN, INTERPOLATE_INTENSITY

    monoEIC: np.ndarray = rawEIC[1]
    rt, intensity = monoEIC[:, 0], monoEIC[:, 1]

    monofit = fitMonoEnvelope(
        rt,
        intensity,
        interpolate=INTERPOLATE_INTENSITY,
        use_quadrature=USE_QUAD,
        peptide=peptide,
    )
    if monofit.fail:
        return None, monofit.fail
    eicIds = (rt >= monofit.lBoundary) & (rt <= monofit.rBoundary)
    intensity = intensity[eicIds]
    if WITH_ORIGIN:
        im = np.c_[np.ones(len(intensity), dtype=np.float32), intensity]
    else:
        im = intensity.reshape(-1, 1)

    intensities = rawEIC[:, eicIds, 1]
    # float[N=maxIso+2,3] # columns: adj_rsquared, slope (beta), alpha
    isotopeRegressions = fitAllIntensities(im, intensities)

    alpha, slopes = isotopeRegressions[:, 2], isotopeRegressions[:, 1]
    anynan = np.isnan(slopes)
    nfailed = np.sum(anynan)
    if nfailed == len(slopes):
        return None, 1 << FAIL_E_EICS

    a = alpha * (monofit.rBoundary - monofit.lBoundary)
    isotopeEnvelopes = ensure_pos(a + monofit.area * slopes)

    maxPeakArea = isotopeEnvelopes[1:].max()
    mono = isotopeEnvelopes[1]
    inv_ratio = isotopeEnvelopes[0] / mono if mono > 0.0 else np.inf
    adjustedRsq = isotopeRegressions[:, 0].astype(np.float32)
    avg_rsq = np.average(adjustedRsq[2:])  # skip -1 and mono
    return (
        IsotopeEnvelope(
            adjustedRsq=adjustedRsq,
            isotopeEnvelopes=isotopeEnvelopes.astype(np.float32),
            # mu, sigma, scale, baseline
            monoFitParams=monofit.popt.astype(
                np.float32,
            ),  # for plotting the fitted gaussian
            inv_ratio=inv_ratio,
            monoPeakArea=monofit.area,
            maxPeakArea=maxPeakArea,
            sigma=monofit.sigma,
            avg_rsq=float(avg_rsq),
        ),
        monofit.fail,
    )


EPS = 1e-10


def labelledEnvelopeCalculation(
    peptide: str,
    maxIso: int,
    isotopeEnvelopes: np.ndarray,
    settings: PeptideSettings,
) -> tuple[LabelledEnvelope, int]:
    assert len(isotopeEnvelopes) == maxIso + 2
    isotopeEnvelopes = isotopeEnvelopes[1:]  # skip -1 mzDiff

    pepinfo = PeptideInfo(peptide, settings)
    enrichments, isotopeEnvelopeBasis = make_envelope_array(
        pepinfo,
        maxIso,
    )

    labelledEnvelopes, nnls_residual = nnls(isotopeEnvelopeBasis, isotopeEnvelopes)

    # ord=1 so that we have labelledEnvelopes like probabilities
    totalNNLSWeight = norm(labelledEnvelopes, ord=1) + EPS
    totalIntensityWeight = norm(isotopeEnvelopes, ord=2) + EPS

    # this is the same as LPF (other authors had different definitions of RIA)
    # ord=1
    relativeIsotopeAbundance = 1.0 - labelledEnvelopes[0] / totalNNLSWeight

    labelEnrichment2 = (enrichments @ labelledEnvelopes) / totalNNLSWeight
    labelEnrichment2 = min(
        max(0, labelEnrichment2),
        settings.maximumLabelEnrichment,
    )

    # this is mystifing
    # theoreticalMaxEnrichment = elementCount * totalNNLSWeight
    # labelEnrichment = (
    #     (np.array(range(len(labelledEnvelope))) * labelledEnvelope).sum()
    #     / theoreticalMaxEnrichment
    #     * settings.maximumLabelEnrichment
    # )

    theoreticalDist = isotopeEnvelopeBasis @ labelledEnvelopes

    heavyDistribution = heavy_dist(
        pepinfo,
        isotopeEnvelopes,
    )
    nmax = len(isotopeEnvelopes)
    # nmax = max(len(theoreticalDist), len(heavyDistribution), len(isotopeEnvelopes))
    theoreticalDist = resize(theoreticalDist, nmax)
    heavyDistribution = resize(heavyDistribution, nmax)
    # isotopeEnvelopes = resize(isotopeEnvelopes, nmax)

    def fit() -> float:
        res = pearsonr(heavyDistribution, theoreticalDist)
        if np.isnan(res.statistic):  # type: ignore
            return 0.0
        return res.statistic  # type: ignore

    def fit2() -> float:
        res = pearsonr(isotopeEnvelopes, theoreticalDist)
        if np.isnan(res.statistic):  # type: ignore
            return 0.0
        return res.statistic  # type: ignore

    heavyCor, fail = catch_warnings(
        fit,
        peptide,
        "labelledEnvelopeCalculation::pearsonr[%s]: %s",
    )
    fail = fail << FAIL_W_PEARSON
    heavyCor2, fail2 = catch_warnings(
        fit2,
        peptide,
        "labelledEnvelopeCalculation::pearsonr2[%s]: %s",
    )
    fail |= fail2 << FAIL_W_PEARSON2

    return (
        LabelledEnvelope(
            labelledEnvelopes=labelledEnvelopes.astype(np.float32),
            theoreticalDist=theoreticalDist.astype(np.float32),
            relativeIsotopeAbundance=relativeIsotopeAbundance,
            enrichment=labelEnrichment2,
            # labelEnrichment2=labelEnrichment2,
            heavyCor=heavyCor,
            heavyCor2=heavyCor2,
            nnls_residual=nnls_residual,
            totalNNLSWeight=totalNNLSWeight,  # type: ignore
            totalIntensityWeight=totalIntensityWeight,  # type: ignore
        ),
        fail,
    )


def fitEnvelope(
    peptide: str,
    rawEIC: np.ndarray,  # [N==pep.maxIso+2,len(rt),2]
    settings: PeptideSettings,
) -> tuple[Envelope | None, int]:
    """Fit envelopes to raw EIC matrix of [mzranges, rt, intensity]"""
    iso, faile = fitIsotopeEnvelopes(rawEIC, peptide)
    if iso is None:
        return None, faile
    maxIso = len(rawEIC) - 2
    assert maxIso == len(iso.isotopeEnvelopes) - 2
    # heavy, failh = fitHeavyEnvelope(pep.peptide, iso)
    labelled, faill = labelledEnvelopeCalculation(
        peptide,
        maxIso,
        iso.isotopeEnvelopes,
        # heavy,
        settings,
    )
    return Envelope.make_all(iso, labelled), faill | faile
