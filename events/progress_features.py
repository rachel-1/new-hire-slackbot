"""
Implement the following state machine.
trigger | resulting state     | action on user input
-------------------------------------------
        | (1)'sleep'          | ignore
9am     | (2)'asked_goal'     | if != "same": store in /current_goal/
        |                     | else: increment days_stuck
        |                     | if days_stuck > 3: nudge to ask a q
        |                     | go to (1)
5pm     | (3)'asked_progress' | ignore input, go to (1)
"""
import datetime
import json

from django.conf import settings
from slackclient import SlackClient

from events.models import User

SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)

with open("events/progress_strings.json") as f:
    all_strings = json.load(f)

def progress_channel_handler(scheduler, user, slack_message):
    """
    Handle user messages in their personal progress channel.
    """
    if user.progress_prompt_state == 'sleep':
        next_time = datetime.datetime.now()
        scheduler.add_job(ask_daily_goal, 'date',
                          run_date=next_time,
                          args=[scheduler, user.slack_user_id])
        pass # weren't expecting anything from user
    elif user.progress_prompt_state == 'asked_goal':
        if slack_message['event']['text'].lower() != 'same':
            user.current_goal = slack_message['event']['text']
            user.days_stuck = 0
        else:
            user.days_stuck += 1
            print("user.days_stuck: ", user.days_stuck) # TODO - remove debug statement
            if user.days_stuck > 3:
                Client.api_call(method='chat.postMessage',
                                channel=user.progress_channel,
                                text=all_strings['q_nudge'])
        user.progress_prompt_state = 'sleep'
    elif user.progress_prompt_state == 'asked_progress':
        # not currently saving this data; just for user to see
        user.progress_prompt_state = 'sleep'
    else:
        raise Exception("Unknown state '{}' in progress state machine".format(user.progress_prompt_state))
    user.save()

def ask_daily_goal(scheduler, user_id):
    user = User.objects.get(slack_user_id=user_id)

    bot_text = all_strings['daily_goal_prompt']
    
    result = Client.api_call(method='chat.postMessage',
                    channel=user.progress_channel,
                    text=bot_text)

    user.progress_prompt_state = 'asked_goal'
    user.save()

    next_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
    scheduler.add_job(ask_daily_progress, 'date',
                      run_date=next_time,
                      args=[scheduler, user_id])

def ask_daily_progress(scheduler, user_id):
    user = User.objects.get(slack_user_id=user_id)
    bot_text = all_strings['daily_progress_prompt']
    
    result = Client.api_call(method='chat.postMessage',
                    channel=user.progress_channel,
                    text=bot_text)

    user.progress_prompt_state = 'asked_progress'
    user.save()

    next_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
    scheduler.add_job(ask_daily_goal, 'date',
                      run_date=next_time,
                      args=[scheduler, user_id])

