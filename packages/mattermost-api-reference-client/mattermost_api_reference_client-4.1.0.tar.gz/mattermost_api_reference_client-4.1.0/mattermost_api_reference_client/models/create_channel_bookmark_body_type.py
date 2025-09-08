from enum import Enum


class CreateChannelBookmarkBodyType(str, Enum):
    FILE = "file"
    LINK = "link"

    def __str__(self) -> str:
        return str(self.value)
