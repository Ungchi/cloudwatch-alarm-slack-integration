from enum import IntEnum, unique


@unique
class AlarmStopStatus(IntEnum):
    NO = 1
    TEMPORARY = 2
    PERMANENT = 3


def get_alarm_stop_status(alarm_stop_second: int) -> AlarmStopStatus:
    """
    ttl -2: key 가 없는 상황, -1: key는 있는데 ttl이 없는 경우, 양수: key도 있고 ttl 도 있고
    :param alarm_stop_second: Redis f"cloudWatch:alarm:{alarm_name}" ttl 값
    """
    if alarm_stop_second == -2:
        return AlarmStopStatus.NO
    elif alarm_stop_second == -1:
        return AlarmStopStatus.PERMANENT
    else:
        return AlarmStopStatus.TEMPORARY
