from http import HTTPStatus

from requests import Response

from logger import log


class SlackException(Exception):
    def __init__(self, response: dict):
        self.msg = f'Slack error response - {response.get("error")}'
        super(SlackException, self).__init__(self.msg)


def slack_api(func):
    def wrapper(*args, **kwargs):
        response: Response = func(*args, **kwargs)
        try:
            result = response.json()
        except Exception as ex:
            log.error(f'Slack response json decode error - {ex}')
            result = dict(error=response.text)
        if response.status_code != HTTPStatus.OK or result.get('error'):
            log.error()
            raise SlackException(result)
        log.debug(f'Slack request success - {result}')
        return response

    return wrapper
