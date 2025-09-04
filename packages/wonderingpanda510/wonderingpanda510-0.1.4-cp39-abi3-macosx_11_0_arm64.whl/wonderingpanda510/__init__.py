from wonderingpanda510._core import hello_from_bin
from . import differential, matrix
from .matrix import rowswap, rowscale, rowreplacement, rref

__all__ = ["hello", "differential", "matrix",
           "rowswap", "rowscale", "rowreplacement", "rref"]

def hello() -> str:
    return hello_from_bin()
