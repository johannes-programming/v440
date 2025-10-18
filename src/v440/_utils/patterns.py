import re
from typing import *

from v440._utils.Cfg import Cfg

QUAL: re.Pattern = re.compile(
    r"(?P<pre>%s)?(?P<post>%s)?(?P<dev>%s)?"
    % (
        Cfg.cfg.data["patterns"]["PRE"],
        Cfg.cfg.data["patterns"]["POST"],
        Cfg.cfg.data["patterns"]["DEV"],
    ),
    re.VERBOSE,
)
