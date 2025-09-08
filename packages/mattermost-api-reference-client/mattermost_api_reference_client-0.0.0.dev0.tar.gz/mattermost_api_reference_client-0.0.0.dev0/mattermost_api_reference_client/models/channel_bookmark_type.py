from enum import Enum


class ChannelBookmarkType(str, Enum):
    FILE = "file"
    LINK = "link"

    def __str__(self) -> str:
        return str(self.value)
