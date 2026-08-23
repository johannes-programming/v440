from typing import reveal_type

import datahold

import v440.abc.CoreABC
import v440.abc.ListABC

reveal_type(datahold.MutableListSlot.copy)
reveal_type(v440.abc.CoreABC.CoreABC.copy)
reveal_type(v440.abc.ListABC.ListABC.__type__)
