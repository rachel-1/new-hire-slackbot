import json
from datetime import date
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient

from events.models import User

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

    # Check if event is that a new member was added to the workspace
    # and if so, greet user

    # This code is only used for dev. So I don't have to add a new user
    # every time I want to test. Commented block below will get this stuff replaced in later.
    event_message = slack_message.get('event')
    print('EVENT_MESSAGE is:', event_message)
    conversation_open = Client.api_call(method='conversations.open',
                                            users='USCT3P11D',
                                            return_im=True)
    user_bot_dm_id = conversation_open['channel']['id']
    if not User.objects.filter(bot_dm_id=user_bot_dm_id).exists():
        new_user = User(slack_user_id=event_message['user'],
                        slack_team_id='team_id',
                        username='kelseysdisplayname',
                        real_name='kelseysrealname',
                        join_date=date.today(),
                        bot_dm_id=user_bot_dm_id,
                        greet_stage=1)
        new_user.save()
        Client.api_call(method='chat.postMessage',
                        channel=user_bot_dm_id,
                        text='who is your manager?')

#     user_bot_dm_id = conversation_open['channel']['id']
    # if event_message['type'] == 'team_join':
    #     user_id = event_message['user']['id']
    #     user_real_name = event_message['user']['real_name']
    #     team_id = event_message['user']['team']
    #     user_display_name = event_message['user']['profile']['display_name']
    #     print("TEAM JOINED")
    #     print("user_real_name", user_real_name)
    #     # channel = event_message.get('channel')
    #     bot_text = all_strings['greeting_string'].format(user_real_name)
    #     conversation_open = Client.api_call(method='conversations.open',
    #                                             users=user_id,
    #                                             text=bot_text,
    #                                             return_im=True)
    #     user_bot_dm_id = conversation_open['channel']['id']
    #     #TODO: check if conversation_open returns anything
    #     print("USER BOT DM ID", user_bot_dm_id)
    #     new_user = User(slack_user_id=user_id,
    #                     slack_team_id=team_id,
    #                     username=user_display_name,
    #                     real_name=user_real_name,
    #                     join_date=date.today(),
    #                     bot_dm_id=user_bot_dm_id
    #                     greet_stage=1)
    #     new_user.save()
    #     Client.api_call(method='chat.postMessage',
    #                     channel=user_bot_dm_id,
    #                     text=bot_text)
    #     return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_200_OK)

def get_manager(request):
    print("in get_manager now ")
    slack_message = request.data
    event_message = slack_message.get('event')
    if event_message is not None:
        if event_message['type'] == 'message':
            print("step 1")
            #get user with event_message['user'] and check if they are in greet stage 1
            # Check if the sender is a new hire
            if User.objects.filter(slack_user_id=event_message['user']).exists() and \
                User.objects.filter(bot_dm_id=event_message['channel']).exists():
                print("step 2")

                this_user = User.objects.get(slack_user_id=event_message['user'])
                if this_user.greet_stage == 1:
                    print("user just said manager is ", event_message['text'])
                    Client.api_call(method='chat.postMessage',
                                    channel=this_user.bot_dm_id,
                                    text="that is your manager?")
