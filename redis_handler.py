import redis

from config import settings

rd = redis.StrictRedis(host=settings.redis_url, port=settings.redis_port, db=0)
REDIS_KEY = 'cloudwatch:alarm:{}'


def get_alarm_stop_second(alarm_name: str) -> int:
    return rd.ttl(REDIS_KEY.format(alarm_name))


def delete_alarm_key(alarm_name: str):
    rd.delete(REDIS_KEY.format(alarm_name))


def set_and_expire_alarm_key(alarm_name: str, ttl: int):
    rd.set(REDIS_KEY.format(alarm_name), 1)
    if ttl > 0:
        rd.expire(REDIS_KEY.format(alarm_name), ttl)
