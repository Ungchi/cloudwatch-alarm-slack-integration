from enum import unique, IntEnum


@unique
class AlarmType(IntEnum):
    ALARM = 1
    WARNING = 2
    OK = 3
    INSUFFICIENT_DATA = 4
