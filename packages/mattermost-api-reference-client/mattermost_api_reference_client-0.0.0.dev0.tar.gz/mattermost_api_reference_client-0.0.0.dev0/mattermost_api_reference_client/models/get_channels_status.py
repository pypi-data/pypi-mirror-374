from enum import Enum


class GetChannelsStatus(str, Enum):
    ALL = "all"
    FINISHED = "Finished"
    INPROGRESS = "InProgress"

    def __str__(self) -> str:
        return str(self.value)
