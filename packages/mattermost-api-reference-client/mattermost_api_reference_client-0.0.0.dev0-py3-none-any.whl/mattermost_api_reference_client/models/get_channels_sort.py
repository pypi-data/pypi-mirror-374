from enum import Enum


class GetChannelsSort(str, Enum):
    CREATE_AT = "create_at"
    END_AT = "end_at"
    ID = "id"
    NAME = "name"
    OWNER_USER_ID = "owner_user_id"
    TEAM_ID = "team_id"

    def __str__(self) -> str:
        return str(self.value)
