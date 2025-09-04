from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import pandas as pd

from .fitenvelopes import fails
from .logger import show_fit_warnings
from .logger import show_log
from .pepxml import compute_maxIso
from .pepxml import compute_modcol
from .pepxml import compute_mz
from .pepxml import getpepxml
from .plotting import FIGSIZE
from .plotting import pepsize
from .plotting import plot_all
from .plotting import plotEICS
from .plotting import plotFittedEnvelopes
from .plotting import plotIntensities
from .plotting import plotLabelledEnvelope
from .pymz import compute_rt
from .pymz import MZI
from .pymz import mzml_calc_pep_envelopes
from .pymz import mzml_create
from .resourcefiles import MzMLResourceFileLocal
from .resourcefiles import PepXMLResourceFileLocal
from .utils import PeptideSettings

if TYPE_CHECKING:
    from matplotlib.figure import Figure


@dataclass(kw_only=True)
class PlotOptions:
    figsize: tuple[float, float] = FIGSIZE
    with_rsq: bool = True


class PlotView:
    def __init__(
        self,
        row: pd.Series,
        settings: PeptideSettings,
        *,
        plot_options: PlotOptions = PlotOptions(),
    ):
        self.row = row
        self.settings = settings
        self.plot_options = plot_options
        self.figsize = self.plot_options.figsize

    def plot_all(self) -> Figure:
        t = plot_all(self.row, self.settings, figsize=self.figsize, layout=(2, 2))  # type: ignore
        return t[0]

    def plotEICS(self) -> Figure:
        return plotEICS(self.row, figsize=self.figsize).get_figure()  # type: ignore

    def plotFittedEnvelopes(self) -> Figure:
        return plotFittedEnvelopes(
            self.row,  # type: ignore
            self.settings,
            figsize=self.figsize,
            with_rsq=self.plot_options.with_rsq,
        ).get_figure()

    def plotLabelledEnvelope(self) -> Figure:
        return plotLabelledEnvelope(
            self.row,  # type: ignore
            self.settings,
            figsize=self.figsize,
        ).get_figure()

    def plotIntensities(self) -> Figure:
        return plotIntensities(self.row, None, figsize=self.figsize).get_figure()  # type: ignore

    def plotNNLS(self) -> Figure:
        from .utils import PeptideInfo
        from .alt_fit import make_envelope_array

        info = PeptideInfo(self.row.peptide, self.settings)
        maxIso = round(self.row.maxIso)

        enrichment, m = make_envelope_array(info, maxIso)

        df = pd.DataFrame(m, columns=[str(round(x, 4)) for x in enrichment])
        df.index.name = "Iso"
        df.columns.name = "enrichment"
        n, e = self.settings.labelledIsotopeNumber, self.settings.labelledElement
        title = f"$^{{{n}}}{e}$ {pepsize(self.row.peptide)}[maxIso={maxIso}]"
        return df.plot(figsize=self.figsize, title=title).get_figure()  # type: ignore


class TurnoverView:
    def __init__(
        self,
        pepxmlfile: Path | str,
        mzmlfile: Path | str,
        settings: PeptideSettings,
        *,
        cache_dir: str | Path | None = None,
        quiet: bool = False,
        plot_options: PlotOptions = PlotOptions(),
    ):
        mzml = MzMLResourceFileLocal(mzmlfile, cache_dir=cache_dir)
        pep = PepXMLResourceFileLocal(pepxmlfile, cache_dir=cache_dir)
        self.settings = settings
        df = None

        if not pep.cache_ok() or not mzml.cache_ok() and not quiet:
            with show_log():
                if not mzml.cache_ok():
                    mzml_create(mzml)
                if not pep.cache_ok():
                    df = getpepxml(pep)

        if not mzml.cache_ok():  # pragma: no cover
            mzml_create(mzml)
        self.mzi = MZI(mzml)
        if df is None:
            df = getpepxml(pep)
        self.pepxml = self.compute(df).reset_index(drop=True)
        self.quiet = quiet
        self.plot_options = plot_options

    def compute(self, pepxml: pd.DataFrame) -> pd.DataFrame:
        pepxml = compute_mz(pepxml)
        pepxml = compute_modcol(pepxml)
        pepxml = compute_maxIso(pepxml, self.settings)
        pepxml = compute_rt(pepxml, self.settings)
        return pepxml

    def create_rec(self, rec: pd.Series) -> tuple[dict[str, Any] | None, int]:
        return mzml_calc_pep_envelopes(self.mzi, rec, self.settings)  # type: ignore

    def plotview(
        self,
        index_or_series: int | pd.Series | pd.DataFrame | str,
        *,
        plot_options: PlotOptions | None = None,
    ) -> PlotView:
        if isinstance(index_or_series, str):
            index_or_series = self.query(index_or_series)

        if isinstance(index_or_series, int):
            s = self.pepxml.loc[index_or_series]
        elif isinstance(index_or_series, pd.DataFrame):
            if len(index_or_series) == 0:
                raise ValueError("zero length dataframe")
            s = index_or_series.iloc[0]
        else:
            s = index_or_series

        if not isinstance(s, pd.Series):
            raise ValueError(
                "index_or_series should be an integer or a Series or a DataFrame",
            )

        if "mzranges" not in s:
            s = self.compute(pd.DataFrame([s])).iloc[0]
        if "eics" not in s:
            with show_fit_warnings(self.quiet):
                rt, fail = self.create_rec(s)
            if rt is None:  # pragma no cover
                raise ValueError("can't fit EICs!")
            rt["fail"] = fail
            rt["fail_reason"] = fails(fail)

            ret = pd.Series(rt)
            s = pd.concat([ret, s])
        return PlotView(
            s,
            self.settings,
            plot_options=plot_options or self.plot_options,
        )

    def get_many(
        self,
        peps: pd.DataFrame,
        include_failures: bool = False,
    ) -> pd.DataFrame:
        retl = []
        if not isinstance(peps, pd.DataFrame):  # pragma: no cover
            raise ValueError("argument is not a DataFrame!")
        with show_fit_warnings(self.quiet):
            for row in peps.itertuples(index=True):
                idx = row[0]
                rt, fail = self.create_rec(row)  # type: ignore
                if rt is not None:
                    rt["peptide_index"] = idx
                    rt["fail"] = fail
                    rt["fail_reason"] = fails(fail)
                    retl.append(rt)
                elif include_failures:  # pragma: no cover
                    rt = {
                        "peptide_index": idx,
                        "fail": fail,
                        "fail_reason": fails(fail),
                    }
                    retl.append(rt)
            if len(retl) == 0:  # pragma: no cover
                return pd.DataFrame()
            df = pd.DataFrame(retl)
            df = df.set_index("peptide_index")

            ret = df.join(peps)
            return ret

    def query(self, query: str, include_failures: bool = False) -> pd.DataFrame:
        return self.get_many(self.pepxml.query(str(query)), include_failures)
