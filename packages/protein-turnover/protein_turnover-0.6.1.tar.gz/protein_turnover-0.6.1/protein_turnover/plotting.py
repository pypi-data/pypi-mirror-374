from __future__ import annotations

from base64 import b64encode
from io import BytesIO
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from scipy import stats

from .alt_fit import natural_dist
from .logger import logger
from .sns import despine
from .utils import ensure_pos
from .utils import PeptideInfo
from .utils import resize

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from .utils import PeptideSettings
    from .types.turnovertype import TurnoverRow
    from .types.turnovertype import TurnoverDict

dpi = 96
FIGSIZE: tuple[float, float] = (1056.0 / dpi, 768.0 / dpi)

EICS_CMAP = plt.get_cmap("viridis")

NEICS_CMAP = len(EICS_CMAP.colors)  # type: ignore

EIC_COLUMNS = ["peptide", "modcol", "eics", "eics_shape", "monoFitParams"]


LABELLED_COLUMNS = [
    "labelledEnvelopes",
    "labelledElementCount",
    "peptide",
    "enrichment",
    "relativeIsotopeAbundance",
    "theoreticalDist",
]


FITTED_COLUMNS = [
    "peptide",
    "modcol",
    "isotopeEnvelopes",
    "maxIso",
    "relativeIsotopeAbundance",
    "enrichment",
    # "adjustedRsq",
]


ALL_COLUMNS = list(set(EIC_COLUMNS) | set(FITTED_COLUMNS) | set(LABELLED_COLUMNS))

# def resize_all(*arrs: np.ndarray) -> list[np.ndarray]:
#     mx = max([len(a) for a in arrs])
#     return [resize(a, mx) for a in arrs]


def pepsize(peptide: str, mx: int = 30) -> str:
    peptide = str(peptide)
    n = len(peptide)
    if n <= mx:
        return peptide
    n = m = (mx - 3) // 2
    n += mx - 2 * n - 3
    return f"{peptide[:n]}...{peptide[-m:]}"


def peptide_legend(peptide: TurnoverRow, enrichment: float | None = None) -> str:
    if enrichment is None:
        enrichment = peptide.enrichment
    if enrichment is not None:
        ie = round(peptide.enrichment * 100, 1)
        ia = round(peptide.relativeIsotopeAbundance * 100, 1)
        return f"{pepsize(peptide.peptide)}\nLPF: {ia}%\nEnrichment: {ie}%"
    else:  # pragma: no cover
        return f"{pepsize(peptide.peptide)},\nunable to estimate enrichment / LPF"


def despine_bottom(ax: Axes) -> None:
    despine(ax=ax, bottom=True, trim=True)


def despine_top(ax: Axes, offset: int = 5) -> None:
    despine(ax=ax, top=True, trim=True, offset=offset)


def plotEICS(
    peptide: TurnoverRow,
    ax: Axes | None = None,
    figsize: tuple[float, float] = FIGSIZE,
) -> Axes:
    from .fitenvelopes import normalIntensityFunction, FAIL_W_CURVE

    pep = peptide.peptide
    mod = peptide.modcol
    eics = peptide.eics
    monoFitParams = peptide.monoFitParams
    fail = len(monoFitParams) == 0  # old way
    if hasattr(peptide, "fail"):  # pragma: no cover
        fail = fail or bool(int(getattr(peptide, "fail")) & (1 << FAIL_W_CURVE))

    # maxInt = eics[0,:, 1].max()
    # ylim = (0, maxInt)
    if ax is None:  # pragma: no cover
        fig = Figure(figsize=figsize)
        ax = fig.subplots()
    ax.set(xlabel="retention time", ylabel="Intensity", title=f"{pepsize(pep)} {mod}")

    m = eics[0]
    rt, im = m[:, 0], m[:, 1]
    ax.plot(rt, im, color="dodgerblue", lw=2)
    oeics = eics[2:]
    step = max(NEICS_CMAP // len(oeics), 1) if len(oeics) else 1

    for idx, e in enumerate(oeics):
        rt, i = e[:, 0], e[:, 1]
        icolor = min(idx * step, NEICS_CMAP - 1)
        ax.plot(
            rt,
            i,
            color=EICS_CMAP.colors[icolor],  # type: ignore
            alpha=0.2,
            linestyle="dashed",
        )

    mono = eics[1]
    rt, im = mono[:, 0], mono[:, 1]
    ax.plot(rt, im, color="red", lw=2)
    d = dict(handlelength=0)
    if not fail:
        i = normalIntensityFunction(rt, *monoFitParams)
        ax.plot(rt, i, color="#8b2252", lw=2)  # violetred4
        ax.legend(labels=["Fitted"], labelcolor="darkgreen", **d)
    else:  # pragma: no cover
        ax.legend(labels=["Bad"], labelcolor="salmon", **d)

    return ax


def intrange(n: int) -> np.ndarray:
    return np.arange(0, n, 1, dtype=np.int32)


def binify(a: np.ndarray, bins: int) -> np.ndarray:
    r = stats.binned_statistic(
        np.arange(len(a)),
        a,
        statistic="sum",
        bins=bins,
    )
    return r.statistic


def plotLabelledEnvelope(
    peptide: TurnoverRow,
    settings: PeptideSettings,
    ax: Axes | None = None,
    scaled: bool = True,
    figsize: tuple[float, float] = FIGSIZE,
    *,
    enrichmentColumns: int = 0,
) -> Axes:
    if ax is None:  # pragma: no cover
        fig = Figure(figsize=figsize)
        ax = fig.subplots()
    if len(peptide.labelledEnvelopes) > 0:
        e = peptide.labelledEnvelopes
        e = e if isinstance(e, np.ndarray) else np.array(e)
        if enrichmentColumns and len(e) != enrichmentColumns:
            e = binify(e, enrichmentColumns)

        x = intrange(len(e))
        enrichments = settings.getEnrichmentsN(len(e))
        if scaled:
            total = e.sum()
            e = e / total
        ax.bar(x, e, color="turquoise", edgecolor="black")
        ax.set_xticks(x)
        ax.set_xticklabels(
            [f"{v:.2f}" for v in enrichments],
            rotation=-90,
        )
        ax.set(xlabel="enrichment")
        if scaled:
            ax.set(ylim=(0.0, 1.0), ylabel="fraction")

    else:  # pragma: no cover
        ie = peptide.labelledElementCount
        x = intrange(ie + 1)
        ax.bar(x, np.repeat(0, ie + 1), color="turquoise")
        ax.set_xticks(x)
    ax.legend(labels=[peptide_legend(peptide)], handlelength=0)
    despine_bottom(ax)
    ax.xaxis.set_ticks_position("none")
    ax.set(title="labelledEnvelopes")
    return ax


def plotFittedEnvelopes(
    peptide: TurnoverRow,
    settings: PeptideSettings,
    ax: Axes | None = None,
    figsize: tuple[float, float] = FIGSIZE,
    *,
    with_rsq: bool = False,
) -> Axes:
    if ax is None:  # pragma: no cover
        fig = Figure(figsize=figsize)
        ax = fig.subplots()

    isotopeEnvelopes = peptide.isotopeEnvelopes
    if len(isotopeEnvelopes) == 0:  # pragma: no cover
        logger.warning("plotFittedEnvelopes[%s]: no envelope!", peptide.peptide)
        return ax

    isotopeEnvelopes = resize(isotopeEnvelopes, peptide.maxIso + 2)

    theoreticalDist = np.array(peptide.theoreticalDist)

    naturalDist = natural_dist(
        PeptideInfo(peptide.peptide, settings),
        peptide.isotopeEnvelopes[1],  # monoScale
    )
    # naturalDist is of length settings.getElementCount(peptideFormula(peptide.peptide))

    naturalDist = resize(naturalDist, peptide.maxIso + 1)
    theoreticalDist = resize(theoreticalDist, peptide.maxIso + 1)

    x = intrange(len(isotopeEnvelopes)) - 1

    heavyDistribution = ensure_pos(isotopeEnvelopes[1:] - naturalDist)
    xm1, x1 = x[:1], x[1:]  # skip negative heavy atom
    ax.set(title=f"{pepsize(peptide.peptide)} {peptide.modcol}")
    ax.bar(
        x1,
        isotopeEnvelopes[1:],
        color="turquoise",
        alpha=1.0,
    )
    ax.bar(x1, heavyDistribution, color="blue", width=0.5, alpha=0.4)
    if with_rsq and hasattr(peptide, "adjustedRsq"):
        adjustedRsq = np.array(peptide.adjustedRsq)
        ax.bar(
            x1,
            adjustedRsq[1:] * isotopeEnvelopes[1],
            color="tomato",
            alpha=0.3,
            width=0.2,
        )

    ax.legend(labels=[peptide_legend(peptide)], handlelength=0, facecolor="none")
    ax.bar(xm1, isotopeEnvelopes[:1], color="red", alpha=0.3)
    ax.bar(x1, -theoreticalDist, color="#98F5FF", alpha=0.3)  # cadetblue1
    nd = resize(naturalDist, len(x) - 1)
    ax.vlines(x1, 0, nd, color="orange", linestyle="dashed")
    ax.scatter(x1, nd, color="orange", marker="o", s=20)

    xlabel = f"number of ${{}}^{{{settings.labelledIsotopeNumber}}}{settings.labelledElement}$ atoms"
    nfailed = np.isnan(isotopeEnvelopes[1:]).sum()
    if nfailed > 0:  # pragma: no cover
        xlabel += f" [{nfailed} failed fits]"
    ax.set(xlabel=xlabel)

    ax.set_xticks(x)

    despine_bottom(ax)
    ax.xaxis.set_ticks_position("none")

    return ax


def plotIntensities(
    peptide: TurnoverRow,  # eics
    eici: list[int] | None = None,
    ax: Axes | None = None,
    figsize: tuple[float, float] = FIGSIZE,
    *,
    with_origin: bool = False,
) -> Axes:
    from scipy.linalg import lstsq

    eics = peptide.eics
    mono_intensity = eics[1, :, 1]
    if with_origin:
        im = np.c_[np.ones(len(mono_intensity)), mono_intensity]
    else:
        im = mono_intensity.reshape(-1, 1)
    x = np.linspace(np.min(mono_intensity), np.max(mono_intensity), num=30)
    if eici is None:
        eici = list(range(2, eics.shape[0]))
    else:  # pragma: no cover
        idx = set(range(2, eics.shape[0]))
        eici = list(sorted(set(eici) & idx))
    if ax is None:  # pragma: no cover
        fig = Figure(figsize=figsize)
        ax = fig.subplots(1, 1)
    # step = max(NEICS_CMAP // len(eici), 1) if len(eici) else 1
    for i in eici:
        ints = eics[i, :, 1]
        _ret = lstsq(im, ints)
        assert _ret is not None
        fit, _residues, _rank, _s = _ret
        if with_origin:
            y = fit[0] + fit[1] * x
        else:
            y = fit[0] * x
        # icolor = min(i * step, NEICS_CMAP - 1)
        # color=EICS_CMAP.colors[icolor]
        ax.scatter(mono_intensity, ints, s=10)
        ax.plot(x, y)
    ax.set(
        title=f"{pepsize(peptide.peptide)} {peptide.modcol}",
        xlabel="mono intensity",
        ylabel="intensity",
    )
    return ax


## @export
def enrichment_plot(
    turn: pd.DataFrame,
    factor: float = 2.0,
    ax: Axes | None = None,
    figsize: tuple[float, float] | None = None,
    column: str = "enrichment",
) -> Axes:
    enrich = turn[column]
    enrich = enrich[enrich.notna()]
    em = enrich.mean()
    esd = enrich.std()
    if ax is None:
        fig = Figure(figsize=figsize if figsize else FIGSIZE)
        ax = fig.subplots(1, 1)

    x = np.linspace(enrich.min() - 3 * esd, enrich.max() + 3 * esd, 40)
    y = stats.norm(em, esd).pdf(x)  # type: ignore

    ax.hist(
        enrich,
        bins=40,
        color="turquoise",
        alpha=0.4,
        density=True,
        edgecolor="#999",
    )
    ax.plot(x, y)
    ax.vlines([em - factor * esd, em + factor * esd], 0, [2.5, 2.5], color="red")
    despine_top(ax, offset=5)
    return ax


def nnls_values(  # pragma: no cover
    df: pd.DataFrame,
    percent: float = 0.01,
) -> pd.Series:
    nnls_residual = df["nnls_residual"]
    if "totalNNLSWeight" in df.columns:
        nnls_residual = nnls_residual / df["totalNNLSWeight"]
    elif "totalIntensityWeight" in df.columns:
        nnls_residual = nnls_residual / df["totalIntensityWeight"]
    nnls_residual = nnls_residual[nnls_residual.notna()]
    if percent == 0.0:
        return nnls_residual

    bins, bounds = np.histogram(nnls_residual, bins=500)

    maxval = bins.max()
    imax = np.argmax(bins == maxval)
    if maxval > 0:
        imin = np.argmin(bins[imax:] / maxval > percent)
    else:
        imin = 0

    idx = min(len(bounds) - 1, int(imax + imin))

    return nnls_residual[nnls_residual < bounds[idx]]


## @export
def nnls_plot(  # ['nnls_residual', 'totalNNLSWeight', 'totalIntensityWeight']
    df: pd.DataFrame,
    ax: Axes | None = None,
    figsize: tuple[float, float] | None = None,
    percent: float = 0.01,
) -> Axes:
    # nnls = nnls_values(df, percent=percent)
    nnls = df["nnls_residual"]

    if ax is None:
        fig = Figure(figsize=figsize if figsize else FIGSIZE)
        ax = fig.subplots(1, 1)
    # mn,mx = nnls_residual.min(), nnls_residual.max()
    ax.hist(nnls, bins="auto", color="turquoise")
    despine(ax, trim=True, offset=5)
    ax.set(ylabel="counts", xlabel="NNLS deviance")
    return ax


def correlation_plot(
    df: pd.DataFrame,
    column: str,
    xlabel: str | None = None,
    ax: Axes | None = None,
    figsize: tuple[float, float] | None = None,
) -> Axes:
    if ax is None:
        fig = Figure(figsize=figsize if figsize else FIGSIZE)
        ax = fig.subplots(1, 1)
    # mn,mx = nnls_residual.min(), nnls_residual.max()
    col = df[column]
    ax.hist(col, bins="auto", color="turquoise")
    despine(ax, trim=True, offset=5)
    ax.set(ylabel="counts", xlabel=xlabel or column)
    return ax


## @export
def plot_all(
    peptide: TurnoverRow,
    settings: PeptideSettings,
    figsize: tuple[float, float] | None = None,
    hspace: float = 0.5,
    *,
    layout: tuple[int, int] = (1, 3),
    enrichmentColumns: int = 0,
) -> tuple[Figure, list[Axes]]:
    r, c = layout
    if figsize is None:
        # width, height
        figsize = c * FIGSIZE[0], r * FIGSIZE[1]

    fig = Figure(figsize=figsize)
    axes = fig.subplots(r, c, gridspec_kw=dict(hspace=hspace), squeeze=False).flatten()

    plotEICS(peptide, ax=axes[0])
    plotFittedEnvelopes(peptide, settings, ax=axes[1])
    plotLabelledEnvelope(
        peptide,
        settings,
        ax=axes[2],
        enrichmentColumns=enrichmentColumns,
    )
    if len(axes) > 3:
        from .config import WITH_ORIGIN

        plotIntensities(peptide, None, ax=axes[3], with_origin=WITH_ORIGIN)
    return fig, axes  # type: ignore


def rename(s: pd.Series, suffix: str = "_me") -> pd.Series:  # pragma: no cover
    r = pd.Series(dtype=object)
    for key in [
        "isotopeEnvelopes",
        "relativeIsotopeAbundance",
        "monoFitParams",
        "eics",
        "labelledEnvelopes",
        "labelledElementCount",
        "enrichment",
        "heavyFitParams",
        "heavyCor",
    ]:
        r[key] = s[key + suffix]

    r.peptide = s.peptide
    r.modcol = s.modcol
    r.maxIso = int(s["maxIso" + suffix])
    return r


def plot_eics_sidebyside(  # pragma: no cover
    b: TurnoverRow,
    suffix: str = "_me",
    figsize: tuple[float, float] = (15.0, 5.0),
) -> tuple[Figure, Axes, Axes]:
    fig = Figure(figsize=figsize)
    [ax1, ax2] = fig.subplots(1, 2)

    plotEICS(b, ax=ax1)
    plotEICS(rename(b, suffix), ax=ax2)  # type: ignore
    return fig, ax1, ax2


def plot_fitted_sidebyside(  # pragma: no cover
    b: TurnoverRow,
    settings: PeptideSettings,
    suffix: str = "_me",
    figsize: tuple[float, float] = (15, 5),
) -> tuple[Figure, Axes, Axes]:
    fig = Figure(figsize=figsize)
    [ax1, ax2] = fig.subplots(1, 2)

    plotFittedEnvelopes(b, settings, ax=ax1)
    plotFittedEnvelopes(rename(b, suffix), settings, ax=ax2)  # type: ignore
    return fig, ax1, ax2


def plot_labelled_sidebyside(  # pragma: no cover
    b: TurnoverRow,
    settings: PeptideSettings,
    suffix: str = "_me",
    figsize: tuple[float, float] = (15, 5),
) -> tuple[Figure, Axes, Axes]:
    fig = Figure(figsize=figsize)
    [ax1, ax2] = fig.subplots(1, 2)

    plotLabelledEnvelope(b, settings, ax=ax1)
    plotLabelledEnvelope(rename(b, suffix), settings, ax=ax2)  # type: ignore
    return fig, ax1, ax2


def plot_fit_arrays(  # pragma: no cover
    row: TurnoverRow,
    suffix: str = "_me",
    figsize: tuple[float, float] = (15, 12),
) -> tuple[Figure, list[list[Axes]]]:
    b: TurnoverDict = row  # type: ignore
    fig = Figure(figsize=figsize)
    axes = fig.subplots(
        5,
        2,
        gridspec_kw=dict(hspace=0.5),
    )
    [[ax1, ax2], [ax3, _ax4], [ax5, ax6], [_ax7, ax8], [ax9, _ax10]] = axes

    def plot_a(name: str, ax: Axes) -> None:
        x = list(range(0, len(b[name])))  # type: ignore
        v = b[name + suffix]  # type: ignore
        if len(x) != len(v):
            ax.set(title=f"bad {name}")
            return
        dodge = np.nanmax(np.abs(v)) / 50
        ax.plot(x, b[name])  # type: ignore
        ax.plot(x, v + dodge)
        ax.set(title=f"{name}")

    def plot_a_col(name: str, ax: Axes, col: int) -> None:
        x = list(range(0, len(b[name][:, col])))  # type: ignore
        v = b[name + suffix][:, col]  # type: ignore
        if len(x) != len(v):
            ax.set(title=f"bad {name}")
            return
        dodge = np.nanmax(np.abs(v)) / 50
        ax.plot(x, b[name][:, col])  # type: ignore
        ax.plot(x, v + dodge)
        ax.set(title=f"{name}")

    def ratio(name: str) -> np.ndarray:
        a = b[name]  # type: ignore
        m = b[name + suffix]  # type: ignore
        if len(a) != len(m):
            return a * 0
        both = (a == 0) & (m == 0)
        ret = m / np.where(a != 0, a, 1e-6)
        if both.sum() > 0:  # 0/0 is 1 !
            ret = np.where(both, 1.0, ret)
        return ret

    def plot_ratio(name: str, ax: Axes) -> None:
        val = b[name]  # type: ignore
        x = list(range(0, len(val)))
        ax.plot(x, ratio(name))
        ax.set(title=f"{name} ratio")

    plot_a_col("isotopeRegressions", ax1, 1)
    ax1.set(title="regression intensity")

    plot_a_col("isotopeRegressions", ax2, 0)
    ax2.set(title="adjusted R-squared")

    plot_a("isotopeEnvelopes", ax3)
    # plot_a("heavyDistribution", ax4)
    # plot_heavy_fit(ax4)
    plot_a("labelledEnvelopes", ax5)
    plot_a("monoFitParams", ax6)
    # plot_a("heavyFitParams", ax7)

    plot_ratio("monoFitParams", ax8)
    plot_ratio("isotopeEnvelopes", ax9)
    # plot_ratio("heavyDistribution", ax10)

    return fig, axes


# for use in jupyter notebooks....
def plot_all_sidebyside(  # pragma: no cover
    b: TurnoverRow,
    settings: PeptideSettings,
) -> tuple[Figure, Figure, Figure, Figure]:
    f1, *_axes = plot_eics_sidebyside(b)
    f2, *_axes = plot_fitted_sidebyside(b, settings)
    f3, *_axes = plot_labelled_sidebyside(b, settings)
    f4, _axes = plot_fit_arrays(b)
    return f1, f2, f3, f4


## @export
def to_image_url(fig: Figure, format: str = "png") -> str:
    out = BytesIO()
    fig.savefig(out, format=format)
    data = f"data:image/{format.lower()};base64,".encode("ascii") + b64encode(
        out.getbuffer(),
    )
    return data.decode("ascii")


## @export
def plotLPF(
    df: pd.DataFrame,  # ['peptide', 'relativeIsotopeAbundance']
    ax: Axes | None = None,
    figsize: tuple[float, float] = (8.0, 1.5),
    sort: bool = True,
) -> Axes:
    if ax is None:
        fig = Figure(figsize=figsize)
        ax = fig.subplots()
    d = df.set_index("peptide")
    d = d["relativeIsotopeAbundance"]
    if sort:
        d = d.sort_values()
    # d.plot(ax=ax, style=".-", color="turquoise")
    d.plot(ax=ax, kind="bar", color="turquoise", edgecolor="black")
    ax.set(ylabel="LPF", ylim=(0, 1), xticks=[])
    despine(
        ax=ax,
        top=True,
        bottom=False,
        trim=True,
        offset=0,
    )
    legend = ax.get_legend()
    if legend is not None:  # pragma: no cover
        legend.remove()

    fig = ax.get_figure()
    if hasattr(fig, "tight_layout"):
        fig.tight_layout()  # type: ignore
    return ax


def plotLogSigmaLPF(
    df: pd.DataFrame,
    ax: Axes | None = None,
    figsize: tuple[float, float] = (8.0, 4.0),
    remove_zero_std: bool = True,
) -> Axes:
    if ax is None:
        fig = Figure(figsize=figsize)
        ax = fig.subplots()
    key = df["lpf_median"] != 0.0
    if remove_zero_std:
        key = key & (df["lpf_std"] != 0.0)
    d = df[key]
    x = np.log((d["lpf_std"] + 1e-4) / (d["lpf_median"]))
    assert isinstance(x, pd.Series)
    x.plot.hist(ax=ax, bins=100, color="turquoise", grid=False)
    despine(ax, trim=True, offset=5)
    ax.set(ylabel="counts", xlabel=r"$log(\sigma/LPF)$")
    return ax
