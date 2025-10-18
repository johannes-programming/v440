import re
from typing import *

from v440._utils.Cfg import Cfg

QUAL: re.Pattern = re.compile(
    Cfg.cfg.data["patterns"]["forms"]["qual"].format(
        **Cfg.cfg.data["patterns"]["atoms"]
    ),
    re.VERBOSE,
)
