from enum import Enum


class UploadSessionType(str, Enum):
    ATTACHMENT = "attachment"
    IMPORT = "import"

    def __str__(self) -> str:
        return str(self.value)
