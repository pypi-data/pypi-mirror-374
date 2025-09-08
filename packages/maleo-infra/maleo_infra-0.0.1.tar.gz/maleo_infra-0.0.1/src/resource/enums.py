from enum import StrEnum


class Status(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "CRITICAL"
    OVERLOAD = "OVERLOAD"
