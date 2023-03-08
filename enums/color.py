from enum import unique

from enums import StrEnum


@unique
class Color(StrEnum):
    RED = '#d9534f'
    YELLOW = '#f0ad4e'
    GREEN = '#5cb85c'
