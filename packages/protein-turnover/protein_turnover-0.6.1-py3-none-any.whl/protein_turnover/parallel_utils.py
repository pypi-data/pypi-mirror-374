from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from concurrent.futures import as_completed
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Callable
from typing import cast
from typing import Iterator
from typing import Sequence
from typing import TypeVar

import pandas as pd

from .resourcefiles import MzMLResourceFile
from .utils import array_split
from .utils import PeptideSettings

Result = TypeVar("Result")


def get_processpool(workers: int) -> ProcessPoolExecutor:
    return ProcessPoolExecutor(max_workers=workers)


def parallel_result(
    exe: list[Callable[[], Result]],
    workers: int = 4,
) -> Iterator[Result]:
    if not exe:  # pragma: no cover
        return
    if workers <= 1:
        for e in exe:
            yield e()
        return
    with get_processpool(workers) as executor:
        futures = [executor.submit(e) for e in exe]
        for future in as_completed(futures):
            yield future.result()


def apply_func(series: pd.Series, func: Callable[..., Result]) -> pd.Series:
    return series.apply(func)  # type: ignore


def parallel_apply(
    series: pd.Series,
    func: Callable[..., Result],
    workers: int,
) -> pd.Series:  # pragma: no cover
    from functools import partial

    if workers <= 1:
        return apply_func(series, func)

    dfs: list[Callable[[], pd.Series]]

    dfs = [
        partial(apply_func, cast(pd.Series, sdf), func)
        for sdf in array_split(series, workers)
    ]

    return pd.concat(
        list(parallel_result(dfs, workers)),
        axis=0,
        ignore_index=False,
    )


class TaskBase(ABC):
    mzml: MzMLResourceFile

    @abstractmethod
    def task_run(self) -> pd.DataFrame: ...  # pragma: no cover


@dataclass
class TaskData:
    pepxml_df: pd.DataFrame
    mzml: MzMLResourceFile
    settings: PeptideSettings
    level: int = 0
    number_of_bg_processes: int = 1

    def mem(self) -> int:  # pragma: no cover
        return self.pepxml_df.memory_usage(deep=True).sum()


class Task(TaskData, TaskBase):
    pass


def parallel_tasks(
    tasks: Sequence[TaskBase],
    *,
    workers: int = 4,
) -> Iterator[tuple[pd.DataFrame, MzMLResourceFile]]:
    if not tasks:
        return

    if workers <= 1 or len(tasks) == 1:
        for task in tasks:
            yield task.task_run(), task.mzml
        return
    # ProcessPoolExecutor re-intialize loggers in the worker processes
    # with initialize function?
    nworkers = min(len(tasks), workers)

    with get_processpool(nworkers) as executor:
        futures = {executor.submit(t.task_run): t for t in tasks}
        for future in as_completed(futures):
            yield future.result(), futures[future].mzml
