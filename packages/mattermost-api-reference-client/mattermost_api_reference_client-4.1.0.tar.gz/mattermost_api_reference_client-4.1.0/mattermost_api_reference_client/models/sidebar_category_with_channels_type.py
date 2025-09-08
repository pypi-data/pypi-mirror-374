from enum import Enum


class SidebarCategoryWithChannelsType(str, Enum):
    CHANNELS = "channels"
    CUSTOM = "custom"
    DIRECT_MESSAGES = "direct_messages"
    FAVORITES = "favorites"

    def __str__(self) -> str:
        return str(self.value)
