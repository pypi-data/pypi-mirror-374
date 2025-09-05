from __future__ import annotations

import operator
import string
import types
from typing import *

from v440.core.VersionError import VersionError

SEGCHARS = string.ascii_lowercase + string.digits


def digest(old: Any, /) -> types.FunctionType:
    byNone: Any = getattr(old, "byNone", None)
    byInt: Any = getattr(old, "byInt", None)
    byList: Any = getattr(old, "byList", None)
    byStr: Any = getattr(old, "byStr", None)

    def new(*args: Any, **kwargs: Any) -> Any:
        args: list = list(args)
        value: Any = args.pop()
        ans: Any
        if value is None:
            ans = byNone(*args, **kwargs)
        elif isinstance(value, int):
            value = int(value)
            ans = byInt(*args, value, **kwargs)
        elif isinstance(value, str) or not hasattr(value, "__iter__"):
            value = str(value).lower().strip()
            ans = byStr(*args, value, **kwargs)
        else:
            value = list(value)
            ans = byList(*args, value, **kwargs)
        return ans

    new.__name__ = old.__name__
    return new


def literal(value: Any, /) -> str:
    value = segment(value)
    if type(value) is str:
        return value
    e = "%r is not a valid literal segment"
    e = VersionError(e % value)
    raise e


def numeral(value: Any, /) -> int:
    value = segment(value)
    if type(value) is int:
        return value
    e = "%r is not a valid numeral segment"
    e = VersionError(e % value)
    raise e


def segment(value: Any, /) -> Any:
    try:
        return _segment(value)
    except:
        e = "%r is not a valid segment"
        e = VersionError(e % value)
        raise e from None


@digest
class _segment:
    def byNone() -> None:
        return

    def byInt(value: Any, /) -> Any:
        if value < 0:
            raise ValueError
        return value

    def byStr(value: Any, /) -> Any:
        if value.strip(SEGCHARS):
            raise ValueError(value)
        ans: Any
        if value.strip(string.digits):
            ans = value
        elif value == "":
            ans = 0
        else:
            ans = int(value)
        return ans


def torange(key: Any, length: Any) -> range:
    start: Any = key.start
    stop: Any = key.stop
    step: Any = key.step
    if step is None:
        step = 1
    else:
        step = operator.index(step)
        if step == 0:
            raise ValueError
    fwd: bool = step > 0
    if start is None:
        start = 0 if fwd else (length - 1)
    else:
        start = operator.index(start)
    if stop is None:
        stop = length if fwd else -1
    else:
        stop = operator.index(stop)
    if start < 0:
        start += length
    if start < 0:
        start = 0 if fwd else -1
    if stop < 0:
        stop += length
    if stop < 0:
        stop = 0 if fwd else -1
    ans: range = range(start, stop, step)
    return ans
