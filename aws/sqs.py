import json

import boto3

from config import settings

sqs = boto3.client('sqs')


def send_message_to_alert_sqs(message, delay_second=300):
    """
    alert sqs 에 메세지 전송 함수
    :param message: sns message
    :param delay_second: sqs 발송 지연 시간, 최대 900초
    """
    delay_second = min(delay_second, 900)
    sqs.send_message(
        QueueUrl=settings.alert_sqs_url,
        DelaySeconds=delay_second,
        MessageBody=json.dumps(message)
    )


def get_sqs_message(event):
    """
    SQS body 파싱 함수
    :param event: SQS 로 트리거 되어 들어온 event
    :return: SQS body
    """
    return json.loads(event['Records'][0]['body'])
