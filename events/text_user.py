import json
from events.models import User
from django.conf import settings
from slackclient import SlackClient

def get_goals(user_id):
    with open("events/strings.json") as f:
        all_strings = json.load(f)
        info = all_strings['goal_setting']
    
    # send message
    SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
    Client = SlackClient(SLACK_BOT_USER_TOKEN)
    Client.api_call(method='chat.postMessage',
                    #channel=user.prof_dev_channel,
                    channel='CS0908BAP',
                    text=info['intro'])

def send_prof_dev_info(user_id):
    print("user_id: ", user_id) # TODO - remove debug statement

    user = User.objects.get(slack_user_id=user_id)
    print("user: ", user) # TODO - remove debug statement
    print("user.prof_dev_stage: ", user.prof_dev_stage) # TODO - remove debug statement

    # TODO
    if user.prof_dev_stage == 2:
        user.prof_dev_stage = 0
    
    index = str(user.prof_dev_stage)
    
    with open("events/strings.json") as f:
        all_strings = json.load(f)
        info = all_strings['professional_development'][index]

    print("info: ", info) # TODO - remove debug statement

    user.type = 'intern' # TODO
    assert user.type in info

    # send message
    SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
    Client = SlackClient(SLACK_BOT_USER_TOKEN)
    for msg in ['description', 'link', 'action']:
        bot_text = info[user.type].get(msg)
        if bot_text is None: continue
        Client.api_call(method='chat.postMessage',
                        #channel=user.prof_dev_channel,
                        channel='CS0908BAP',
                        text=bot_text)
    
    user.prof_dev_stage += 1
    user.save()

