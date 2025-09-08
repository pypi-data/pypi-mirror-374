from enum import Enum


class ListPlaybookRunsStatusesItem(str, Enum):
    FINISHED = "Finished"
    INPROGRESS = "InProgress"

    def __str__(self) -> str:
        return str(self.value)
