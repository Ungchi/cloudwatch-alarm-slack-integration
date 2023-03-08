from aws.cloudwatch import change_alarm_threshold
from logger import log
from redis_handler import set_and_expire_alarm_key
from slack import open_modal, post_message


class SlackBot:
    def __init__(self, params):
        self.params = params
        self.action = params['actions'][0]
        self.callback_id = params.get('callback_id', self.action.get('action_id'))
        log.debug(f'callback_id - {self.callback_id}')
        self.user_id = params['user']['id']
        self.username = params['user']['name']
        self.original_message = params.get('original_message', params.get('message'))

    def callback(self):
        if self.callback_id == 'change_threshold':
            return self.run_change_threshold_callback()
        elif self.callback_id == 'stop_alarm':
            return self.mute_alarm()
        elif self.callback_id == 'alarm_setting':
            open_modal(self.params)
        return {'statusCode': 200, 'body': 'ok'}

    def run_change_threshold_callback(self):
        """
        slack modal 창에서 임계값 수정시 실행되는 콜백 함수
        image alt_text 영역에 channel 과 메세지 thread_ts 값이 설정되어 있어 이를 확인해 thread message 를 남긴다.
        :param params: API Gateway body 에 payload value
        """
        message_info = self.params['view']['blocks'][1]['alt_text'].split(';')
        channel = message_info[0]
        thread_ts = message_info[1]
        previous_value = self.params['view']['blocks'][3]['element']['placeholder']['text']
        value = float(self.action['value'])
        alarm_name = self.params['view']['blocks'][0]['text']['text']
        change_alarm_threshold(alarm_name, value)
        message = {
            'channel': channel,
            'thread_ts': thread_ts,
            'text': f'<@{self.username}> Change {alarm_name} threshold {previous_value} to {value}'
        }
        post_message(message)
        return {'statusCode': 200, 'body': 'ok'}

    def mute_alarm(self):
        """
        slack modal 창에서 알람 중지 선택 시 실행되는 콜백 함수
        image alt_text 영역에 channel 과 메세지 thread_ts 값이 설정되어 있어 이를 확인해 thread message 를 남긴다.
        :param params: API Gateway body 에 payload value
        """
        message_info = self.params['view']['blocks'][1]['alt_text'].split(';')
        channel = message_info[0]
        thread_ts = message_info[1]
        selected_text = self.action['selected_option']['text']['text']
        value = int(self.action['selected_option']['value'])
        alarm_name = self.params['view']['blocks'][0]['text']['text']
        ttl = value * 60
        set_and_expire_alarm_key(alarm_name, ttl)
        message = {
            'channel': channel,
            'thread_ts': thread_ts,
            'text': f'<@{self.username}> Mute alarm *{alarm_name}* for {selected_text}'
        }
        post_message(message)
        return {'statusCode': 200, 'body': 'ok'}
