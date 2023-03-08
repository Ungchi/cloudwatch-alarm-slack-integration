from config import settings
from enums import AlarmType, Color, SlackIcon


def get_slack_message(alarm_type, sns_message, image_url, additional_log=''):
    namespace = sns_message['Namespace']
    alarm_name = sns_message['AlarmName']
    state_reason = sns_message['NewStateReason']
    state_change_time = sns_message['StateChangeTime']
    threshold = sns_message['Trigger']['Threshold']
    if alarm_type == AlarmType.ALARM:
        color = Color.RED
        icon = SlackIcon.SIREN
    elif alarm_type == AlarmType.WARNING:
        color = Color.YELLOW
        icon = SlackIcon.WARNING
    else:
        color = Color.GREEN
        icon = SlackIcon.CHECK_BOX
    attachment = {
        'color': color,
        'fallback': f'{icon} {alarm_name}',
        'blocks': [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f'{icon} <https://ap-northeast-2.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-2#alarm:name={alarm_name} | {alarm_name}>'
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": state_reason
                }
            },
            {
                "type": "section",
                'fields': [
                    {
                        "type": "mrkdwn",
                        "text": f"*타입*\n{namespace}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*발생시점*\n{state_change_time}",
                    }
                ],
            },
            {
                "type": "image",
                "image_url": image_url,
                "alt_text": f'{alarm_name};{threshold}'
            }
        ],
    }
    if alarm_type != AlarmType.OK:
        if additional_log:
            attachment['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": additional_log
                }
            })
        attachment['blocks'].append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "알람 설정",
                        "emoji": True
                    },
                    "value": "alarm_setting",
                    "action_id": "alarm_setting"
                }
            ]
        })
    message = {'attachments': [attachment], 'channel': settings.slack_channel}
    return message


def get_modal_message(params):
    alt_text = params['message']['attachments'][0]['blocks'][5]['alt_text']
    alarm_name, threshold = alt_text.split(';')
    image_url = params['message']['attachments'][0]['blocks'][5]['image_url']
    channel_id = params['channel']['id']
    message_ts = params['container']['message_ts']
    modal_message = {
        "type": "modal",
        "title": {
            "type": "plain_text",
            "text": "CloudWatch Alarm Setting",
            "emoji": True
        },
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": alarm_name
                }
            },
            {
                "type": "image",
                "image_url": image_url,
                "alt_text": f"{channel_id};{message_ts}"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "알람 중지"
                },
                "accessory": {
                    "type": "static_select",
                    "action_id": "stop_alarm",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Choose list",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "30분"
                            },
                            "value": "30"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "1시간"
                            },
                            "value": "60"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "2시간"
                            },
                            "value": "120"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "6시간"
                            },
                            "value": "360"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "12시간"
                            },
                            "value": "720"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "24시간"
                            },
                            "value": "1440"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "48시간"
                            },
                            "value": "2880"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "계속"
                            },
                            "value": "-1"
                        },
                    ]
                }
            },
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "change_threshold",
                    "placeholder": {
                        "type": "plain_text",
                        "text": threshold
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": f"임계값(Threshold) 수정[기존: {threshold}]",
                }
            }
        ]
    }
    return modal_message
