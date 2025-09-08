from enum import Enum


class ItemSetStateBodyNewState(str, Enum):
    CLOSED = "closed"
    IN_PROGRESS = "in_progress"
    VALUE_0 = ""

    def __str__(self) -> str:
        return str(self.value)
