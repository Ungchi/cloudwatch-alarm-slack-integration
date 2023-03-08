from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    slack_channel: str = Field(env='SLACK_CHANNEL', default='')
    user_token: str = Field(env='SLACK_USER_TOKEN', default='')
    bot_token: str = Field(env='SLACK_BOT_TOKEN', default='')
    redis_url: str = Field(env='REDIS_URL', default='')
    redis_port: int = Field(env='REDIS_PORT', default=6379)
    alert_sqs_url: str = Field(env='ALERT_SQS_URL', default='')
    repeat_sns_arn: str = Field(env='REPEAT_SNS_ARN', default='')
    single_sns_arn: str = Field(env='SINGLE_SNS_ARN', default='')


settings = Settings()
