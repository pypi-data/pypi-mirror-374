#
# Copyright (C) 2019-2025  Leo Singer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Tools for progress bars"""

try:
    from billiard import Pool
except ImportError:
    from multiprocessing import Pool
from heapq import heappop, heappush
from operator import length_hint

import numpy as np
from tqdm.auto import tqdm

from .. import omp

__all__ = ("progress_map", "progress_map_vectorized")


class WrappedFunc:
    def __init__(self, func):
        self.func = func

    def __call__(self, i_args):
        i, args = i_args
        return i, self.func(*args)


class WrappedFuncWithLength:
    def __init__(self, func):
        self.func = func

    def __call__(self, i_args):
        i, args = i_args
        return len(args[0]), (i, self.func(*args))


def _get_total_estimate(*iterables):
    """Estimate total loop iterations for mapping over multiple iterables."""
    return min(length_hint(iterable) for iterable in iterables)


def _results_in_order(completed):
    """Put results back into order and yield them as quickly as they arrive."""
    heap = []
    current = 0
    for i_result in completed:
        i, result = i_result
        if i == current:
            yield result
            current += 1
            while heap and heap[0][0] == current:
                _, result = heappop(heap)
                yield result
                current += 1
        else:
            heappush(heap, i_result)
    assert not heap, "The heap must be empty"


_in_pool = False
"""Flag to prevent nested multiprocessing pools."""

_jobs = 1
_pool = None


def _init_process():
    """Disable OpenMP when using multiprocessing."""
    global _in_pool
    omp.num_threads = 1
    _in_pool = True


def progress_map(func, *iterables, jobs=1, **kwargs):
    """Map a function across iterables of arguments.

    Parameters
    ----------
    func : callable
        Function to evaluate.
    iterables
        Input argument iterables.
    jobs : int
        Number of subprocesses.
    kwargs : dict
        Additional keyword arguments passed to :obj:`tqdm.tqdm`.

    This is comparable to :meth:`astropy.utils.console.ProgressBar.map`, except
    that it is implemented using :mod:`tqdm` and so provides more detailed and
    accurate progress information.
    """
    global _jobs, _pool
    total = _get_total_estimate(*iterables)
    if _in_pool or jobs == 1:
        yield from tqdm(map(func, *iterables), total=total, **kwargs)
    else:
        if jobs != _jobs:
            if _pool is not None:
                _pool.close()
            _pool = Pool(jobs, _init_process)
            _jobs = jobs

        # Chunk size heuristic reproduced from
        # https://github.com/python/cpython/blob/v3.13.1/Lib/multiprocessing/pool.py#L481-L483.
        chunksize, extra = divmod(total, len(_pool._pool) * 4)
        if extra or chunksize == 0:
            chunksize += 1

        yield from _results_in_order(
            tqdm(
                _pool.imap_unordered(
                    WrappedFunc(func), enumerate(zip(*iterables)), chunksize=chunksize
                ),
                total=total,
                **kwargs,
            )
        )


def progress_map_vectorized(func, *iterables, jobs=1, nout=1, **kwargs):
    """Map a Numpy vectorized function across iterables of arguments.

    Optional parallelization is applied across the first axis of the
    iterables.

    Parameters
    ----------
    func : callable
        Function to evaluate.
    iterables
        Input argument arrays.
    jobs : int
        Number of subprocesses.
    nout : int
        Number of outputs of the function.
    kwargs : dict
        Additional keyword arguments passed to :obj:`tqdm.tqdm`.

    Notes
    -----
    All of the iterables must have equal length.
    """
    global _jobs, _pool
    if _in_pool or jobs == 1:
        return func(*iterables)
    else:
        # Check that all iterables have the same length
        total, *rest = (len(iterable) for iterable in iterables)
        for i, item in enumerate(rest):
            if item != total:
                raise ValueError(
                    f"Length of argument {i} ({item}) does not match length of argument 0 ({total})"
                )

        if jobs != _jobs:
            if _pool is not None:
                _pool.close()
            _pool = Pool(jobs, _init_process)
            _jobs = jobs

        # Chunk size heuristic reproduced from
        # https://github.com/python/cpython/blob/v3.13.1/Lib/multiprocessing/pool.py#L481-L483.
        chunks = min(total, len(_pool._pool) * 4)

        with tqdm(total=total, **kwargs) as progress:

            def update(n_result):
                n, result = n_result
                progress.update(n)
                return result

            result = list(
                _results_in_order(
                    update(n_result)
                    for n_result in _pool.imap_unordered(
                        WrappedFuncWithLength(func),
                        enumerate(
                            zip(
                                *(
                                    np.array_split(iterable, chunks)
                                    for iterable in iterables
                                )
                            )
                        ),
                        chunksize=1,
                    )
                )
            )

            if nout == 1:
                return np.concatenate(result)
            else:
                return np.column_stack(result)
