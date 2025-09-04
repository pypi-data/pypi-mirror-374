from __future__ import annotations

from dataclasses import replace
from functools import wraps
from typing import Any
from typing import Callable

import click


# from https://stackoverflow.com/questions/56185880/commands-with-multiple-common-options-going-into-one-argument-using-custom-decor
# This drags in scipy and pandas and numpy from imports above
# *and* depends on ATOMICPROPERTIES via getNr which drags in numpy again


def setting_options(func: Callable[..., Any]) -> Callable[..., Any]:
    # don't want to import .utils since this will drag in scipy, numpy etc
    # see .utils.NAMES
    NAMES = ["C", "H", "O", "N", "P", "S", "Se"]

    @wraps(func)
    @click.option(
        "-e",
        "--element",
        "labelledElement",
        type=click.Choice(NAMES),
        help="heavy isotope",
    )
    @click.option(
        "--isotope",
        "labelledIsotopeNumber",
        type=click.IntRange(1),
        help="isotope number",
    )
    @click.option(
        "--mztol",
        "mzTolerance",
        type=click.FloatRange(0.0),
        help="m/z tolerance in PPM",
    )
    @click.option(
        "--rttol",
        "rtTolerance",
        type=click.FloatRange(0.0),
        help="retention time tolerance in seconds",
    )
    @click.option(
        "--enrich-cols",
        "enrichmentColumns",
        type=int,
        help="number of enrichment columns (if zero use maxIso if 1 use elementCount; defaults to 10)",
    )
    def distill_settings(
        labelledElement: str,
        labelledIsotopeNumber: int,
        mzTolerance: float,
        rtTolerance: float,
        enrichmentColumns: int,
        **kwargs: Any,
    ) -> Any:
        # this function is being called so we can import now
        from .utils import PeptideSettings, getDefaultIsotopeNr, okNr

        settings = PeptideSettings()

        def rep(**kwargs: Any) -> PeptideSettings:
            return replace(settings, **kwargs)

        try:
            if labelledElement is not None:
                settings = rep(
                    labelledElement=labelledElement,
                    labelledIsotopeNumber=getDefaultIsotopeNr(labelledElement),
                )
            if labelledIsotopeNumber is not None:
                if labelledIsotopeNumber not in okNr(settings.labelledElement):
                    raise click.BadParameter(
                        f"unknown isotope {settings.labelledElement}[{labelledIsotopeNumber}]",
                        param_hint="isotope",
                    )

                settings = rep(
                    labelledIsotopeNumber=labelledIsotopeNumber,
                )
            if mzTolerance is not None:
                settings = rep(mzTolerance=mzTolerance / 1.0e6)

            if rtTolerance is not None:
                settings = rep(rtTolerance=rtTolerance)
            if enrichmentColumns is not None:
                settings = rep(enrichmentColumns=enrichmentColumns)
        except ValueError as e:  # pragma: no cover
            click.secho(f"{e}", fg="red", err=True, bold=True)
            raise click.Abort()
        kwargs["settings"] = settings
        return func(**kwargs)

    return distill_settings
