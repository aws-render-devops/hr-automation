from slack_sdk.web.async_client import AsyncWebClient

from app.consts import SlackChannels
from settings import settings


client = AsyncWebClient(token=settings.slack_bot_token)


class SlackHelper:

    @classmethod
    async def _send_message(cls, channel, message):
        return await client.chat_postMessage(
            channel=channel,
            text=message,
            link_names=True,
        )

    @classmethod
    async def send_test_warning_message(cls):
        message = f'@channel :warning:\n' \
                  f'Test warning message! \n'
        return await cls._send_message(channel=SlackChannels.HR_AUTOMATION, message=message)
