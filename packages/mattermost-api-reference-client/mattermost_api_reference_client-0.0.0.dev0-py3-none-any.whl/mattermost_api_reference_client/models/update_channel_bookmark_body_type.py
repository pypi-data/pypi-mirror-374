from enum import Enum


class UpdateChannelBookmarkBodyType(str, Enum):
    FILE = "file"
    LINK = "link"

    def __str__(self) -> str:
        return str(self.value)
