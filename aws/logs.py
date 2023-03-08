from datetime import datetime

import boto3

from logger import log

logs = boto3.client('logs', region_name='ap-northeast-2')
TEN_MINUTE = 600000


def get_lambda_error_log(lambda_name: str):
    error_messages = ''
    now_timestamp = int(datetime.now().timestamp() * 1000)
    print(f'람다 로그 수집 - {lambda_name}')
    try:
        log_events = logs.filter_log_events(
            logGroupName=f'/aws/lambda/{lambda_name}',
            startTime=now_timestamp - TEN_MINUTE,
            endTime=now_timestamp,
            filterPattern='ERROR',
            limit=1,
        )
        print('log_events', log_events)
        if log_events['events']:
            error_messages = f"```{log_events['events'][0]['message']}```"
    except:
        log.error('람다 로그 수집 실패', exc_info=True)
    return error_messages


if __name__ == '__main__':
    get_lambda_error_log('cafemon-crawler-stg-lambda')
