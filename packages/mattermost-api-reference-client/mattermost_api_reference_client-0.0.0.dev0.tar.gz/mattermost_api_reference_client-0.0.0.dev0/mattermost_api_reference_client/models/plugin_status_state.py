from enum import Enum


class PluginStatusState(str, Enum):
    FAILEDTOSTART = "FailedToStart"
    FAILEDTOSTAYRUNNING = "FailedToStayRunning"
    NOTRUNNING = "NotRunning"
    RUNNING = "Running"
    STARTING = "Starting"
    STOPPING = "Stopping"

    def __str__(self) -> str:
        return str(self.value)
