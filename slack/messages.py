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
                        "text": f"*Namespace*\n{namespace}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*StateChangeTime*\n{state_change_time}",
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
                        "text": "Settings",
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
    alt_text = params['message']['attachments'][0]['blocks'][3]['alt_text']
    alarm_name, threshold = alt_text.split(';')
    image_url = params['message']['attachments'][0]['blocks'][3]['image_url']
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
                    "text": "Mute monitor"
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
                                "text": "10m"
                            },
                            "value": "10"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "30m"
                            },
                            "value": "30"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "1h"
                            },
                            "value": "60"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "2h"
                            },
                            "value": "120"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "6h"
                            },
                            "value": "360"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "12h"
                            },
                            "value": "720"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "24h"
                            },
                            "value": "1440"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Forever"
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
                    "text": f"Change Threshold[Now: {threshold}]",
                }
            }
        ]
    }
    return modal_message
