import json
from events.models import User
from django.conf import settings
from slackclient import SlackClient

import datetime

SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)
    
def get_goals(user_id):
    result = Client.api_call(method='chat.postMessage',
                             channel="GSGG2KC7J",
                             #channel=user.prof_dev_channel,
                             text='test')
    return
    user = User.objects.get(slack_user_id=user_id)
    
    with open("events/strings.json") as f:
        all_strings = json.load(f)
        info = all_strings['goal_setting']
    
    # send message
    result = Client.api_call(method='chat.postMessage',
                             channel=user.prof_dev_channel,
                             text=info['intro'])
    
    # reply in thread with examples
    Client.api_call(method='chat.postMessage',
                             channel=user.prof_dev_channel,
                             text=info['examples'],
                             thread_ts=result['ts'])
    
    user.goals_thread = result['ts']
    user.save()
    
def remind_about_goals(user_id):
    user = User.objects.get(slack_user_id=user_id)

    result = Client.api_call(method='chat.getPermalink',
                             channel=user.prof_dev_channel,
                             message_ts=user.goals_thread)

    with open("events/strings.json") as f:
        all_strings = json.load(f)

    bot_text = all_strings['goal_reminder']+result['permalink']
    Client.api_call(method='chat.postMessage',
                    channel=user.prof_dev_channel,
                    text=bot_text,
                    unfurl_links=True)

def send_prof_dev_info(user_id):
    user = User.objects.get(slack_user_id=user_id)

    # TODO
    if user.prof_dev_stage == 2:
        user.prof_dev_stage = 0
    
    index = str(user.prof_dev_stage)
    
    with open("events/strings.json") as f:
        all_strings = json.load(f)
        info = all_strings['professional_development'][index]

    for msg in ['info', 'action']:
        bot_text = info['intern'].get(msg)
        if bot_text is None: continue
        Client.api_call(method='chat.postMessage',
                        channel=user.prof_dev_channel,
                        text=bot_text)
        bot_text = info['manager'].get(msg)
        if bot_text is None: continue
        Client.api_call(method='chat.postMessage',
                        channel=user.manager_prof_dev_channel,
                        text=bot_text)

    
    user.prof_dev_stage += 1
    user.save()

def setup_articles(scheduler, user_id):
    # TODO - adding this causes the jobs to be run multiple times
    #scheduler.add_jobstore(DjangoJobStore(), "default")
    print("Adding jobs...")
    next_date = datetime.datetime.now()
    for i in range(2):
        scheduler.add_job(send_prof_dev_info, 'date', run_date=next_date, args=[user_id])
        # TODO - no guarantee one job will finish before the next
        next_date += datetime.timedelta(seconds=20)
    print("Jobs added!")
