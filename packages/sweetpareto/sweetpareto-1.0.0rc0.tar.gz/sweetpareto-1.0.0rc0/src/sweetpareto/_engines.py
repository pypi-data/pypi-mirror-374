# Copyright Andrew Johnson, 2025
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
import math
import operator
import typing

from sweetpareto.types import EngineT, SupportedEngineT, ValueT, VectorT

if typing.TYPE_CHECKING:
    from collections.abc import Iterator


def engine_factory(engine: SupportedEngineT, /) -> EngineT:
    """Factory for determining how the pareto indices should be found.

    Parameters
    ----------
    engine
        If a string, name of the engine to be discovered and used.
        Otherwise, should be a function that can be called like
        ``indices: list[int] = engine(x, y, maxx, maxy)``.
        The integers should be the pareto front
        ``x[indices]`` and ``y[indices]``  that maximizes or minimizes
        ``x`` and ``y`` according to the ``maxx`` and ``maxy`` booleans.

    Returns
    -------
    Callable[[np.ndarray, np.ndarray, bool, bool], list[int]]

    Raises
    ------
    KeyError
        If a string is provided and it cannot be interpreted.
    """
    if not isinstance(engine, str):
        return engine
    if engine == "python":
        return _pure_py_front_indices
    msg = f"Engine {engine} is not available. Only 'python' is supported at this time."
    raise KeyError(msg)


def _pure_py_front_indices(x: VectorT, y: VectorT, maxx: bool, maxy: bool, /) -> list[int]:
    rows = x.argsort()
    if maxx:
        rows = rows[::-1]
    points: list[int] = []
    # Use the same iterator so when we resume at the next row
    # after the find the first non-nan pair
    riter: Iterator[ValueT] = iter(rows)
    for row in riter:
        if not (math.isnan(x[row]) or math.isnan(y[row])):
            points.append(row)
            break
    else:
        return points
    current_y = y[points[0]]
    check_dominated = operator.gt if maxy else operator.lt
    for ix in riter:
        new_y = y[ix]
        if math.isnan(x[ix]) or math.isnan(new_y):
            continue
        is_dominated = check_dominated(new_y, current_y)
        if is_dominated:
            if x[ix] == x[points[-1]]:
                points.pop()
            current_y = new_y
            points.append(ix)
    return points
