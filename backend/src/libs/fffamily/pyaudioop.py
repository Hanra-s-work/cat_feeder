"""Minimal shim providing a subset of the stdlib `audioop` API.

This file is intended as a temporary compatibility layer for
environments where the C-extension `audioop` is missing (e.g. custom
Python builds or stripped-down containers). It implements a few small
helpers that `pydub` commonly calls: `rms`, `max` and `avg`.

This is a light-weight pure-Python implementation and may be slower
than the C-extension for large buffers; it is only intended to
unblock imports and normal usage of `pydub` in CI/dev containers.
"""
from __future__ import annotations

import math
from typing import Iterable, List


def _samples_from_fragment(fragment: bytes, width: int) -> Iterable[int]:
    import struct

    if width == 1:
        if not fragment:
            return ()
        fmt = f"{len(fragment)}b"
        return struct.unpack(fmt, fragment)
    if width == 2:
        count = len(fragment) // 2
        if count == 0:
            return ()
        fmt = f"<{count}h"
        return struct.unpack(fmt, fragment)
    if width == 3:
        samples: List[int] = []
        for i in range(0, len(fragment), 3):
            b = fragment[i:i+3]
            if len(b) < 3:
                break
            # sign-extend the most-significant byte to 4 bytes (little-endian)
            sign = b[2] & 0x80
            ext = b"\xff" if sign else b"\x00"
            val = int.from_bytes(b + ext, "little", signed=True)
            samples.append(val)
        return samples
    if width == 4:
        count = len(fragment) // 4
        if count == 0:
            return ()
        fmt = f"<{count}i"
        return struct.unpack(fmt, fragment)
    raise ValueError("width must be 1..4 bytes per sample")


def rms(fragment: bytes, width: int) -> int:
    """Return the root-mean-square of audio samples in `fragment`.

    Parameters mirror the stdlib `audioop.rms(fragment, width)`.
    """
    samples = _samples_from_fragment(fragment, width)
    total = 0
    n = 0
    for s in samples:
        total += s * s
        n += 1
    if n == 0:
        return 0
    mean = total / n
    return int(math.sqrt(mean))


def max(fragment: bytes, width: int) -> int:  # noqa: A003 - mirrors audioop API
    samples = _samples_from_fragment(fragment, width)
    maxv = 0
    for s in samples:
        v = abs(s)
        if v > maxv:
            maxv = v
    return maxv


def avg(fragment: bytes, width: int) -> int:
    samples = _samples_from_fragment(fragment, width)
    total = 0
    n = 0
    for s in samples:
        total += s
        n += 1
    if n == 0:
        return 0
    return int(total / n)


__all__ = ["rms", "max", "avg"]
