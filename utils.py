import base64
from datetime import datetime, timedelta


def base64_decoding(target_text):
    target_text_utf8_encoded = target_text.encode("UTF-8")
    target_text_base64_decoded = base64.b64decode(target_text_utf8_encoded)
    return target_text_base64_decoded.decode("UTF-8")


def utc_to_kst(utc_time):
    utc_datetime = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S.%f+0000')
    kst_datetime = utc_datetime + timedelta(hours=9)
    return kst_datetime.strftime('%Y-%m-%d %H:%M:%S')


def is_lambda_alarm(message):
    trigger = message['Trigger']
    return trigger['Namespace'] == 'AWS/Lambda'


def get_lambda_name(message):
    trigger = message['Trigger']
    lambda_name = next((d['value'] for d in trigger['Dimensions'] if d['name'] == 'FunctionName'), '')
    return lambda_name
