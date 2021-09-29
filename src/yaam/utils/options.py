from enum import Enum
from typing import Set

class Option(Enum):
    
    UPDATE_ADDONS = (0, set(["-update-addons", "/update-addons"]))

    def __eq__(self, o: object) -> bool:
        if isinstance(o, Option):
            return self.value == o.value
        else:
            return False

    @property
    def aliases(self) -> Set[str]:
        return self.content[1]

    @property
    def value(self) -> int:
        return self.content[0]

    @property
    def content(self) -> tuple:
        return super().value

