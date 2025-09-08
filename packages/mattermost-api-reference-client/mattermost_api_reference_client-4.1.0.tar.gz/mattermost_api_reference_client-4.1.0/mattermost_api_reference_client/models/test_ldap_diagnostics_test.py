from enum import Enum


class TestLdapDiagnosticsTest(str, Enum):
    ATTRIBUTES = "attributes"
    FILTERS = "filters"
    GROUP_ATTRIBUTES = "group_attributes"

    def __str__(self) -> str:
        return str(self.value)
