import json

from utils import utc_to_kst


def get_sns_message(event):
    """
    SNS message 파싱 함수
    Namespace 의 경우 없을 수도 있다.
    :param event: SNS 로 트리거 되어 들어온 event
    :return: SNS message, StateChangeTime, Namespace
    """
    message = json.loads(event['Records'][0]['Sns']['Message'])
    message['StateChangeTime'] = utc_to_kst(message['StateChangeTime'])
    message['Namespace'] = str(message['Trigger'].get('Namespace'))
    return message
