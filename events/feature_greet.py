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

# Is run when event is team_join
def send_greeting_message(event_message):
    all_strings = {}
    with open('events/strings.json') as json_file:
        all_strings = json.load(json_file)
    user_id = event_message['user']['id']
    user_real_name = event_message['user']['real_name']
    team_id = event_message['user']['team_id']
    user_display_name = event_message['user']['profile']['display_name']
    conversation_open = Client.api_call(method='conversations.open',
                                            users=user_id,
                                            return_im=True)
    user_bot_dm_id = conversation_open['channel']['id']
    if not User.objects.filter(bot_dm_id=user_bot_dm_id).exists():
        # Bot has never chatted with this new teammate before
        new_user = User(slack_user_id=user_id,
                        slack_team_id=team_id,
                        username=user_display_name,
                        real_name=user_real_name,
                        join_date=date.today(),
                        bot_dm_id=user_bot_dm_id,
                        greet_stage=1)
        new_user.save()
        Client.api_call(method='chat.postMessage',
                        channel=user_bot_dm_id,
                        text=all_strings['greeting']['greeting_string'].format(user_display_name))
        Client.api_call(method='chat.postMessage',
                        channel=user_bot_dm_id,
                        text=all_strings['greeting']['manager_inquiry'])
    return Response(status=status.HTTP_200_OK)

# TODO: need to specify when this is run in views.py
def get_manager(event_message):
    all_strings = {}
    with open('events/strings.json') as json_file:
        all_strings = json.load(json_file)
    # if event_message['type'] == 'message':
    # Check if the sender is a new hire in stage of no manager yet
    if User.objects.filter(slack_user_id=event_message['user']).exists() and \
        User.objects.get(slack_user_id=event_message['user']).greet_stage == 1:
        this_user = User.objects.get(slack_user_id=event_message['user'])
        manager_name = event_message['text']
        manager_id = find_id_from_name(manager_name)
        if len(manager_id) == 0:
            # Manager not found
            Client.api_call(method='chat.postMessage',
                        channel=this_user.bot_dm_id,
                        text=all_strings['greeting']['manager_retry'])
        else:
            Client.api_call(method='chat.postMessage',
                        channel=this_user.bot_dm_id,
                        text=all_strings['greeting']['manager_successful'])
            this_user.manager_name = manager_name
            this_user.manager_id = manager_id
            this_user.greet_stage = 2
            this_user.save()
            Client.api_call(method='chat.postMessage',
                        channel=this_user.bot_dm_id,
                        text=all_strings['greeting']['meet_greet'])
            first_name = this_user.real_name.split()[0]
            Client.api_call(method='chat.postMessage',
                        channel=this_user.bot_dm_id,
                        text=all_strings['greeting']['intro_channels'].format(first_name, first_name, first_name))
            create_user_channels(this_user.slack_user_id, first_name, all_strings)
    return Response(status=status.HTTP_200_OK)

def find_id_from_name(name):
    all_users = Client.api_call(method='users.list')
    while True:
        if not all_users['ok']:
            break
        for member_info in all_users['members']:
            if member_info['is_bot']:
                continue
            if 'real_name' in member_info and name.lower() == member_info['real_name'].lower():
                return member_info['id']
            if name.lower() == member_info['profile']['real_name'].lower():
                return member_info['id']
            if name.lower() == member_info['profile']['display_name'].lower():
                return member_info['id']
        next_cursor = all_users['response_metadata']['next_cursor']
        if len(next_cursor) == 0:
            # No more
            break
        all_users = Client.api_call(method='users.list', cursor=next_cursor)
    return ""

def create_user_channels(user_id, first_name, all_strings):
    this_user = User.objects.get(slack_user_id=user_id)
    prof_dev = Client.api_call(method='conversations.create',
                name='{}-pro-dev'.format(first_name),
                is_private=True)
    if 'channel' in prof_dev:
        # Channel with same name doesn't already exist
        Client.api_call(method='conversations.invite',
                channel=prof_dev['channel']['id'],
                users=user_id)
        progress = Client.api_call(method='conversations.create',
                    name='{}-progress'.format(first_name),
                    is_private=True)
        Client.api_call(method='conversations.invite',
                channel=progress['channel']['id'],
                users=user_id)
        questions = Client.api_call(method='conversations.create',
                    name='{}-questions'.format(first_name),
                    is_private=True)
        Client.api_call(method='conversations.invite',
                channel=questions['channel']['id'],
                users=user_id)
        # Send questions channel introduction message
        Client.api_call(method='chat.postMessage',
                    channel=questions['channel']['id'],
                    text=all_strings['questions']['introduction'])
        this_user.prof_dev_channel = prof_dev['channel']['id']
        this_user.progress_channel = progress['channel']['id']
        this_user.questions_channel = questions['channel']['id']
        this_user.save()
