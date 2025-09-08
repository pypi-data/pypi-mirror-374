from enum import Enum


class ListPlaybookRunsSort(str, Enum):
    CREATE_AT = "create_at"
    END_AT = "end_at"
    ID = "id"
    IS_ACTIVE = "is_active"
    NAME = "name"
    OWNER_USER_ID = "owner_user_id"
    TEAM_ID = "team_id"

    def __str__(self) -> str:
        return str(self.value)
