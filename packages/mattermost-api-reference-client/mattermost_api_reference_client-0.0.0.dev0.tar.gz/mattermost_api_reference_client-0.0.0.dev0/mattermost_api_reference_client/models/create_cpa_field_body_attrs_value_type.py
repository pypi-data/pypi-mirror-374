from enum import Enum


class CreateCPAFieldBodyAttrsValueType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"

    def __str__(self) -> str:
        return str(self.value)
