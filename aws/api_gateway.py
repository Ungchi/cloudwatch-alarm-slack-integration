import json
from urllib.parse import parse_qsl

from utils import base64_decoding


def get_api_gateway_params(event: dict) -> dict:
    """
    base64 로 인코딩되어 들어올 경우 body 를 디코딩하고 dict 타입으로 변경, payload value 를 반환한다.
    :param event: API Gateway 로 trigger 될 때 들어오는 event
    :return: body or query parameter value
    """
    is_base64_encoded = event['isBase64Encoded']
    body = event.get('body')
    if is_base64_encoded:
        return json.loads(dict(parse_qsl(base64_decoding(body)))['payload'])
    elif body:
        return json.loads(body)
    return json.loads(event.get('queryStringParameters'))
