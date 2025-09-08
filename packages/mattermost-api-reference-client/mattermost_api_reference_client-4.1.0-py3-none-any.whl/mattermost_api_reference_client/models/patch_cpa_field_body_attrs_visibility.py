from enum import Enum


class PatchCPAFieldBodyAttrsVisibility(str, Enum):
    ALWAYS = "always"
    HIDDEN = "hidden"
    WHEN_SET = "when_set"

    def __str__(self) -> str:
        return str(self.value)
