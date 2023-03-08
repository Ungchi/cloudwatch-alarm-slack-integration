from enum import unique

from enums import StrEnum


@unique
class SlackIcon(StrEnum):
    SIREN = ':rotating_light:'
    WARNING = ':warning:'
    CHECK_BOX = ':white_check_mark:'
    TADA = ':tada:'
    RED_X = ':x:'
