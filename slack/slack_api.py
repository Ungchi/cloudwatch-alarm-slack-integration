import requests

from config import settings
from slack import slack_api, get_modal_message

bot_headers = {
    'Authorization': f'Bearer {settings.bot_token}',
    'Content-type': 'application/json'
}
user_authorization = dict(Authorization=f'Bearer {settings.user_token}')
user_headers = {
    **user_authorization,
    'Content-type': 'application/json'
}
SLACK_POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
SLACK_OPEN_VIEWS_URL = 'https://slack.com/api/views.open'
SLACK_UPLOAD_FILES_URL = 'https://slack.com/api/files.upload'
SLACK_FILE_SHARE_URL = 'https://slack.com/api/files.sharedPublicURL'


@slack_api
def post_message(message):
    return requests.post(SLACK_POST_MESSAGE_URL, headers=bot_headers, json=message)


@slack_api
def open_modal(params):
    trigger_id = params['trigger_id']
    modal_message = get_modal_message(params)
    body = dict(trigger_id=trigger_id, view=modal_message)
    return requests.post(SLACK_OPEN_VIEWS_URL, headers=bot_headers, json=body)


def upload_file(params, image):
    resp = _upload_file(params, image)
    result = resp.json()
    return result['file']['id']


@slack_api
def _upload_file(params, image):
    return requests.post(SLACK_UPLOAD_FILES_URL, headers=user_authorization, params=params, files=image)


def get_file_public_url(file_id):
    resp = _get_file_public_url(file_id)
    result = resp.json()
    permalink_public = result['file']['permalink_public']
    pub_secret = permalink_public.split('-')[-1]
    url_private = result['file']['url_private']
    url_public = f'{url_private}?pub_secret={pub_secret}'
    return url_public


def _get_file_public_url(file_id):
    return requests.post(SLACK_FILE_SHARE_URL, headers=user_headers, json={'file': file_id})
