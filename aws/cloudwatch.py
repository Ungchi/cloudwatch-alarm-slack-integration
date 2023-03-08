import json
import boto3

from enums.comparison_operator import ComparisonOperator
from logger import log
from slack import upload_file, get_file_public_url

cloudwatch = boto3.client('cloudwatch', region_name='ap-northeast-2')

ALLOW_METRIC_KEYS = [
    'AlarmName', 'AlarmDescription', 'ActionsEnabled', 'OKActions', 'AlarmActions', 'InsufficientDataActions',
    'MetricName', 'Namespace', 'Statistic', 'ExtendedStatistic', 'Dimensions', 'Period', 'Unit', 'EvaluationPeriods',
    'DatapointsToAlarm', 'Threshold', 'ComparisonOperator', 'TreatMissingData', 'EvaluateLowSampleCountPercentile',
    'Metrics', 'Tags', 'ThresholdMetricId'
]


def get_cloudwatch_alarm_info(alarm_name: str) -> dict:
    """
    CloudWatch 실시간 데이터를 확인하여 반환한다.
    :param alarm_name: CloudWatch Alarm Name
    :return: CloudWatch Alarm Info
    """
    resp = cloudwatch.describe_alarms(AlarmNames=[alarm_name])
    return resp['MetricAlarms'][0]


def get_metric_image_data(message):
    """
    CloudWatch Metric 그래프 이미지 정보를 확인해 반환한다.
    :param message: sns 에서 message value
    :return: .png 이미지 정보
    """
    trigger = message['Trigger']
    print('trigger', trigger)
    metric = [trigger['Namespace'], trigger['MetricName']]
    for dimension in trigger['Dimensions']:
        metric.append(dimension['name'])
        metric.append(dimension['value'])
    # trigger['Statistic'] = AVERAGE -> Average 변환
    stat = trigger['Statistic'].title()
    metric.append({"stat": stat})
    print(f'metric: {metric}')
    comparison_operator = ComparisonOperator[trigger['ComparisonOperator']].value
    metric_widget = {
        "region": "ap-northeast-2",
        "timezone": "+0900",
        "metrics": [metric],
        "view": "timeSeries",
        "stacked": False,
        "period": trigger['Period'],
        "annotations": {
            "horizontal": [
                {
                    "label": f"{trigger['MetricName']} {comparison_operator}",
                    "value": trigger['Threshold']
                }
            ]
        },
        "title": message["AlarmName"]
    }
    metric = json.dumps(metric_widget)
    image_resp = cloudwatch.get_metric_widget_image(MetricWidget=metric)
    return image_resp['MetricWidgetImage']


def get_metric_image_url(message):
    """
    CloudWatch Metric 이미지를 슬랙에 파일 업로드 후 public url 을 획득한다.
    upload_file 을 통해 바로 슬랙에 올리면 알람 메세지랑 그래프 이미지랑 따로 올라가는 문제로 슬랙에 파일을 업로드만 하고 public url 을 생성한다.
    :param message: sns 에서 message value
    :return: image public url
    """
    metric_image_data = get_metric_image_data(message)
    slack_params = {'filename': f'{message["AlarmName"]}.png'}
    image = {'file': metric_image_data}
    file_id = upload_file(slack_params, image)
    file_url = get_file_public_url(file_id)
    return file_url


def change_alarm_threshold(alarm_name, threshold):
    """
    CloudWatch Alarm Threshold 수정하는 함수
    기존 알람 정보를 가져온 뒤 threshold 값만 변경해 수정한다.
    :param alarm_name: CloudWatch Alarm Name
    :param threshold: CloudWatch Alarm Threshold Value
    """
    alarm_info = get_cloudwatch_alarm_info(alarm_name)
    keys = list(alarm_info.keys())
    for key in keys:
        if key not in ALLOW_METRIC_KEYS:
            alarm_info.pop(key)
    alarm_info['Threshold'] = threshold
    resp = cloudwatch.put_metric_alarm(**alarm_info)
    log.info(f'cloudwatch put_metric_alarm result: {resp}')
