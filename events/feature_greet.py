import json
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings,
                               'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)

# TODO: If you are newly added to the workspace with bot installed,
# the bot will ask you: are you a new hire? And who is your manager


def send_greeting_message(request):
    all_strings = {}
    with open('events/strings.json') as json_file:
        all_strings = json.load(json_file)
    slack_message = request.data
    if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
        return Response(status=status.HTTP_403_FORBIDDEN)
    # Check if event is that a new member was added to the workspace
    # and if so, greet user
    event_message = slack_message.get('event')
    print('EVENT_MESSAGE is:', event_message)
    if event_message['type'] == 'team_join':
        user_id = event_message['user']['id']
        user_real_name = event_message['user']['real_name']
        print("TEAM JOINED")
        print("user_real_name", user_real_name)
        # channel = event_message.get('channel')
        bot_text = all_strings['greeting_string'].format(user_real_name)
        conversation_open = Client.api_call(method='conversations.open',
                                                users=user_id,
                                                text=bot_text,
                                                return_im=True)
        user_bot_im_id = conversation_open['channel']['id']
        #TODO add ^ to the database
        Client.api_call(method='chat.postMessage',
                        channel=user_bot_im_id,
                        text=bot_text)
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_200_OK)
