from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes

# culled from seaborn so we can remove one dependency...


def despine(
    ax: Axes,
    *,
    top: bool = True,
    right: bool = True,
    left: bool = False,
    bottom: bool = False,
    offset: float | dict[str, float] | None = None,
    trim: bool = False,
) -> None:
    A = dict(top=top, bottom=bottom, left=left, right=right)
    for side, aval in A.items():
        # Toggle the spine objects
        is_visible = not aval
        ax.spines[side].set_visible(is_visible)
        if offset is not None and is_visible:
            try:
                val = offset.get(side, 0.0)  # type: ignore
            except AttributeError:
                val = offset
            ax.spines[side].set_position(("outward", val))  # type: ignore

    # Potentially move the ticks
    if left and not right:  # pragma: no cover
        maj_on = any(t.tick1line.get_visible() for t in ax.yaxis.majorTicks)
        min_on = any(t.tick1line.get_visible() for t in ax.yaxis.minorTicks)
        ax.yaxis.set_ticks_position("right")
        for t in ax.yaxis.majorTicks:
            t.tick2line.set_visible(maj_on)
        for t in ax.yaxis.minorTicks:
            t.tick2line.set_visible(min_on)

    if bottom and not top:  # pragma: no cover
        maj_on = any(t.tick1line.get_visible() for t in ax.xaxis.majorTicks)
        min_on = any(t.tick1line.get_visible() for t in ax.xaxis.minorTicks)
        ax.xaxis.set_ticks_position("top")
        for t in ax.xaxis.majorTicks:
            t.tick2line.set_visible(maj_on)
        for t in ax.xaxis.minorTicks:
            t.tick2line.set_visible(min_on)

    if trim:
        # clip off the parts of the spines that extend past major ticks
        xticks = np.asarray(ax.get_xticks())
        if xticks.size:
            firsttick = np.compress(xticks >= min(ax.get_xlim()), xticks)[0]
            lasttick = np.compress(xticks <= max(ax.get_xlim()), xticks)[-1]
            ax.spines["bottom"].set_bounds(firsttick, lasttick)
            ax.spines["top"].set_bounds(firsttick, lasttick)
            newticks = xticks.compress(xticks <= lasttick)
            newticks = newticks.compress(newticks >= firsttick)
            ax.set_xticks(newticks)

        yticks = np.asarray(ax.get_yticks())
        if yticks.size:
            firsttick = np.compress(yticks >= min(ax.get_ylim()), yticks)[0]
            lasttick = np.compress(yticks <= max(ax.get_ylim()), yticks)[-1]
            ax.spines["left"].set_bounds(firsttick, lasttick)
            ax.spines["right"].set_bounds(firsttick, lasttick)
            newticks = yticks.compress(yticks <= lasttick)
            newticks = newticks.compress(newticks >= firsttick)
            ax.set_yticks(newticks)
