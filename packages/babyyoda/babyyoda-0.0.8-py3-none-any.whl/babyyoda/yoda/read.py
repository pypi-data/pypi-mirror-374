from typing import Any

import yoda as yd

from babyyoda.yoda.counter import Counter
from babyyoda.yoda.histo1d import Histo1D
from babyyoda.yoda.histo2d import Histo2D


def read(file_path: str) -> dict[str, Any]:
    """
    Wrap yoda histograms in the by HISTO1D_V2 class
    """

    ret: dict[str, Any] = {}
    for k, v in yd.read(file_path).items():
        if isinstance(v, yd.Histo1D):
            ret[k] = Histo1D(v)
        elif isinstance(v, yd.Histo2D):
            ret[k] = Histo2D(v)
        elif isinstance(v, yd.Counter):
            ret[k] = Counter(v)
        else:
            ret[k] = v
    return ret
