from enum import Enum
from typing import List

class OPTION(Enum):
    
    NO_ARC_DPS = (0, ["-noArcDPS", "/noArcDPS", "-no-arc-dps", "/no-arc-dps"])
    UPDATE_ADDONS = (1, ["-update-addons", "/update-addons"])

    def __eq__(self, o: object) -> bool:
        if isinstance(o, OPTION):
            return self.value[0] == o.value[0]
        else:
            return False

    def aliases(self) -> List[str]:
        return self.value[1]

    @property
    def value(self) -> tuple:
        return super().value