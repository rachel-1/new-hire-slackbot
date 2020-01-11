import datetime
import json

from datetime import date
from datetime import timedelta
from django.conf import settings
from slackclient import SlackClient

from events.models import User
from events.feature_community import pair_members

SLACK_BOT_USER_TOKEN = getattr(settings,
                               'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)

def create_new_hire_channel(scheduler):
    # midnight_today = datetime.datetime.combine(date.today(), datetime.datetime.min.time()) + timedelta(days=1)
    demo_midnight_today = datetime.datetime.now() + timedelta(minutes=5)
    print("CREATE NEW HIRES CHANNEL CALLED!")
    if User.objects.filter(join_date=date.today()).count() <= 1:
        # Only schedule if first user who joined that day
        print("SCHEDULED!!")
        scheduler.add_job(create_channel_and_invite, 'date',
                           run_date=demo_midnight_today,
                           args=['newbies-'+datetime.datetime.now().strftime('%m-%d-%y')])

def create_channel_and_invite(channel_name):
    # today_midnight = datetime.datetime.combine(date.today(), datetime.datetime.min.time()) - timedelta(days=1)
    # tomorrow_midnight = today_midnight + timedelta(days=2)
    all_strings = {}
    with open('events/strings.json') as json_file:
        all_strings = json.load(json_file)
    print("INVITES BEING SENT!!")
    users_joined_today = User.objects.filter(join_date=date.today())
    print("TODAY IS,", date.today())
    print("USERS JOINED TODAY QUERYSET: ", users_joined_today)
    newbies_channel = Client.api_call(method='conversations.create',
                name=channel_name,
                is_private=True)
    if users_joined_today.count() == 1:
        Client.api_call(method='chat.postMessage',
                        channel=users_joined_today[0].bot_dm_id,
                        text=all_strings['greeting']['only_one_join'])
    elif users_joined_today.count() >= 2:
        for user in users_joined_today:
            print("INVITING", user.real_name)
            Client.api_call(method='conversations.invite',
                    channel=newbies_channel['channel']['id'],
                    users=user.slack_user_id)
        pair_members(newbies_channel['channel']['id'], True)
