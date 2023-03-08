from aws.api_gateway import get_api_gateway_params
from aws.cloudwatch import get_cloudwatch_alarm_info, get_metric_image_url
from aws.logs import get_lambda_error_log
from aws.sns import get_sns_message
from aws.sqs import send_message_to_alert_sqs, get_sqs_message
from config import settings
from enums.alarm_stop_status import get_alarm_stop_status, AlarmStopStatus
from enums.alarm_type import AlarmType
from logger import log
from redis_handler import get_alarm_stop_second, delete_alarm_key
from slack import get_slack_message, post_message
from slack.slack_bot import SlackBot
from utils import is_lambda_alarm, get_lambda_name


def lambda_handler(event, context):
    """
    API Gateway, Repeat SNS, Single SNS, Repeat SQS 로 트리거 되어 실행되는 함수
    """
    log.debug(f'event: {event}')
    # Trigger By API Gateway
    if event.get('rawPath'):
        return arch_bot_handler(event)
    event_source = event['Records'][0].get('EventSource') or event['Records'][0].get('eventSource')
    # Trigger By SQS
    if event_source == 'aws:sqs':
        repeat_alarm_sqs(event)
    # Trigger By Repeat SNS
    elif event_source == 'aws:sns' and event['Records'][0]['Sns']['TopicArn'] == settings.repeat_sns_arn:
        repeat_alarm_sns(event)
    # Trigger By Single SNS
    elif event_source == 'aws:sns' and event['Records'][0]['Sns']['TopicArn'] == settings.single_sns_arn:
        single_alarm_sns(event)


def single_alarm_sns(event):
    """
    단일 알람 SNS 처리 함수
    WARNING, OK 한번만 슬랙 메세지를 보내고 종료한다.
    """
    slack_message = get_single_alarm_message(event)
    if slack_message:
        post_message(slack_message)


def get_single_alarm_message(event):
    message = get_sns_message(event)
    alarm_type = AlarmType.WARNING if message['NewStateValue'] == 'ALARM' else AlarmType.OK
    previous_alarm_type = AlarmType[message['OldStateValue']]
    if previous_alarm_type == AlarmType.INSUFFICIENT_DATA and alarm_type == AlarmType.OK:
        return None
    image_url = get_metric_image_url(message)
    lambda_error_log = ''
    if is_lambda_alarm(message):
        lambda_name = get_lambda_name(message)
        lambda_error_log = get_lambda_error_log(lambda_name)
    return get_slack_message(alarm_type, message, image_url, lambda_error_log)


def repeat_alarm_sns(event):
    """
    반복 알람 SNS 처리 함수
    ALARM 상태가 되면 슬랙 메세지를 보내고 SQS 에 delaySecond 를 설정하여 쌓아둔다.
    """
    message = get_sns_message(event)
    alarm_name = message['AlarmName']
    alarm_type = AlarmType[message['NewStateValue']]
    previous_alarm_type = AlarmType[message['OldStateValue']]
    if previous_alarm_type == AlarmType.INSUFFICIENT_DATA and alarm_type == AlarmType.OK:
        return
    alarm_stop_second = get_alarm_stop_second(alarm_name)
    alarm_stop_status = get_alarm_stop_status(alarm_stop_second)
    if alarm_stop_status == AlarmStopStatus.NO:
        image_url = get_metric_image_url(message)
        slack_message = get_slack_message(alarm_type, message, image_url)
        post_message(slack_message)
    if alarm_type == AlarmType.ALARM:
        send_message_to_alert_sqs(message)


def repeat_alarm_sqs(event):
    """
    반복 알람 SNS 처리 함수에서 보낸 메세지를 처리하는 함수
    delaySecond 이후에 트리거되어 ALARM 의 현재 상태를 확인 후 계속 ALARM 상태이면 슬랙 메세지를 보내고 SQS 에 delaySecond 를 설정하여 쌓아둔다.
    슬랙 메세지를 보내기 전 redis에 f'cloudWatch:alarm:{alarm_name}' Key 를 확인하여 알람 일시 중지 상태인지 확인한다.
    """
    message = get_sqs_message(event)
    alarm_name = message['AlarmName']
    alarm_type = AlarmType[get_cloudwatch_alarm_info(alarm_name)['StateValue']]
    alarm_stop_second = get_alarm_stop_second(alarm_name)
    alarm_stop_status = get_alarm_stop_status(alarm_stop_second)
    if alarm_type == AlarmType.ALARM and alarm_stop_status == AlarmStopStatus.NO:
        image_url = get_metric_image_url(message)
        slack_message = get_slack_message(alarm_type, message, image_url)
        post_message(slack_message)
        send_message_to_alert_sqs(message)
    elif alarm_type == AlarmType.ALARM and alarm_stop_status == AlarmStopStatus.TEMPORARY:
        send_message_to_alert_sqs(message, alarm_stop_second)
    elif alarm_stop_status == AlarmStopStatus.PERMANENT:
        delete_alarm_key(alarm_name)


def arch_bot_handler(event):
    """
    아키봇 액션 처리 함수
    """
    params = get_api_gateway_params(event)
    log.debug(f'API Gateway body: {params}')
    bot = SlackBot(params)
    return bot.callback()


if __name__ == '__main__':
    test_event = {'Records': [{'EventSource': 'aws:sns', 'EventVersion': '1.0',
                               'EventSubscriptionArn': 'arn:aws:sns:ap-northeast-2:145972894989:cafemon-alarm-sns:4eb05b76-99bb-4a98-a7da-804c9f5ba594',
                               'Sns': {'Type': 'Notification', 'MessageId': 'd04e9195-5bbc-5fda-ba74-cd1486943a58',
                                       'TopicArn': 'arn:aws:sns:ap-northeast-2:145972894989:cafemon-alarm-sns',
                                       'Subject': 'OK: "partners-sqs-batch-live-lambda-error" in Asia Pacific (Seoul)',
                                       'Message': '{"AlarmName":"partners-sqs-batch-live-lambda-error","AlarmDescription":null,"AWSAccountId":"145972894989","AlarmConfigurationUpdatedTimestamp":"2022-06-28T01:45:48.392+0000","NewStateValue":"OK","NewStateReason":"Threshold Crossed: 1 out of the last 1 datapoints [0.0 (08/03/23 00:45:00)] was not greater than or equal to the threshold (1.0) (minimum 1 datapoint for ALARM -> OK transition).","StateChangeTime":"2023-03-08T00:46:32.006+0000","Region":"Asia Pacific (Seoul)","AlarmArn":"arn:aws:cloudwatch:ap-northeast-2:145972894989:alarm:partners-sqs-batch-live-lambda-error","OldStateValue":"INSUFFICIENT_DATA","OKActions":["arn:aws:sns:ap-northeast-2:145972894989:cafemon-alarm-sns"],"AlarmActions":["arn:aws:sns:ap-northeast-2:145972894989:cafemon-alarm-sns"],"InsufficientDataActions":[],"Trigger":{"MetricName":"Errors","Namespace":"AWS/Lambda","StatisticType":"Statistic","Statistic":"SUM","Unit":null,"Dimensions":[{"value":"partners-sqs-batch-live-lambda","name":"FunctionName"}],"Period":60,"EvaluationPeriods":1,"DatapointsToAlarm":1,"ComparisonOperator":"GreaterThanOrEqualToThreshold","Threshold":1.0,"TreatMissingData":"missing","EvaluateLowSampleCountPercentile":""}}',
                                       'Timestamp': '2023-03-08T00:46:32.065Z', 'SignatureVersion': '1',
                                       'Signature': 'OUtoP5eKMoFeKef6tu12/jSuvs0/PovtaeBDakpe8YgU0G0Y5hcBT8sbuO4lojoo2Y2lVFoXikHSWc3m5N4TdW8WUhrYOpVdGsj0RXFk+j04EhvpuFjzpABRpu0uqnEVLggBLAQG/IHuPOscv+OXQ17Ba03AHFDcqEF+/xPRHvuzVNt0rdW7qxdO6mP5SbP1xVlJ24+/9fako5av8SS3oajYQF4Byw1r/g3J+JKXPKD0xBry0RCzUpG3Wy5lyxlitVvbJ52SPABuNIKsHHKjBFyveoZAkv4fDG93pvpueIKuzsV6f6Ke680AvJ6TD3UEgjSSW8XEpsbsKi1tLBZbbg==',
                                       'SigningCertUrl': 'https://sns.ap-northeast-2.amazonaws.com/SimpleNotificationService-56e67fcb41f6fec09b0196692625d385.pem',
                                       'UnsubscribeUrl': 'https://sns.ap-northeast-2.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:ap-northeast-2:145972894989:cafemon-alarm-sns:4eb05b76-99bb-4a98-a7da-804c9f5ba594',
                                       'MessageAttributes': {}}}]}
    lambda_handler(test_event, None)
