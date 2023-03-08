from enum import unique

from enums import StrEnum


@unique
class ComparisonOperator(StrEnum):
    GreaterThanOrEqualToThreshold = '>='
    GreaterThanThreshold = '>'
    GreaterThanUpperThreshold = '>>'
    LessThanLowerOrGreaterThanUpperThreshold = '< or >'
    LessThanLowerThreshold = '<<'
    LessThanOrEqualToThreshold = '<='
    LessThanThreshold = '<'
