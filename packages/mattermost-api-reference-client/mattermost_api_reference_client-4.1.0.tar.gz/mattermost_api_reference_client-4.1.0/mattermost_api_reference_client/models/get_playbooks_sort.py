from enum import Enum


class GetPlaybooksSort(str, Enum):
    STAGES = "stages"
    STEPS = "steps"
    TITLE = "title"

    def __str__(self) -> str:
        return str(self.value)
