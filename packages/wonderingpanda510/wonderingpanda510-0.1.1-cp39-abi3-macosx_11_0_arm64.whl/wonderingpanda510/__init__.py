from wonderingpanda510._core import hello_from_bin
from . import differential
from .differential.discrete import diff
from . import matrix
from .matrix.elementry import rowswap, rowscale, rowreplacement, rref

def hello() -> str:
    return hello_from_bin()
