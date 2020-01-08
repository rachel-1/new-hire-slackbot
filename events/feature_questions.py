from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings,
'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)

def create_questions(request):
    slack_message = request.data

    if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
        return Response(status=status.HTTP_403_FORBIDDEN)
    # verification challenge
    if slack_message.get('type') == 'url_verification':
        return Response(data=slack_message,
                        status=status.HTTP_200_OK)
    # greet bot
    if 'event' in slack_message:
        event_message = slack_message.get('event')
        print('event_message is:', event_message)
        # ignore bot's own message
        if 'bot_id' in event_message:
            return Response(status=status.HTTP_200_OK)
        # process user's message
        user = event_message.get('user')
        text = event_message.get('text')
        channel = event_message.get('channel')
        bot_text = 'wassup! this is question bot speaking'.format(user)
        if 'hi' in text.lower():
            Client.api_call(method='chat.postMessage',
                            channel=channel,
                            text=bot_text)
            return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_200_OK)