from __future__ import annotations

import operator
from typing import *

from overloadable import Overloadable

from v440._utils.releaseparse import ranging


def getitem_int(data: tuple[int], key: int) -> int:
    if key < len(data):
        return data[key]
    else:
        return 0
