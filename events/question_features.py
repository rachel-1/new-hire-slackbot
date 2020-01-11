import json

from django.conf import settings
from slackclient import SlackClient

from events.models import User

with open("events/strings.json") as f:
    all_strings = json.load(f)

def qs_reminder(user_id):
    SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
    Client = SlackClient(SLACK_BOT_USER_TOKEN)

    user = User.objects.get(slack_user_id=user_id)
        
    #bot_text = all_strings['qs_prompt']
    bot_text = "test"
    Client.api_call(method='chat.postMessage',
                    channel=user.questions_channel,
                    text=bot_text)
