from enum import Enum
from typing import List

class OPTION(List[str], Enum):
    
    NO_ARC_DPS = ["-noArcDPS", "/noArcDPS", "-no-arc-dps", "/no-arc-dps"]
    UPDATE_ADDONS = ["-update-addons", "/update-addons"]

