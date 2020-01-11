from django.conf import settings
from slackclient import SlackClient
import random
import json

SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)

def pair_members(channel_id):
    result = Client.api_call(method='auth.test')
    bot_user_id = result['user_id']
    
    result = Client.api_call(method='conversations.members',
                             channel=channel_id)

    members = result['members']

    random.shuffle(members)

    members.remove(bot_user_id)

    def pairs(lst):
        for i in range(0, len(lst), 2):
            yield lst[i:i + 2]

    pairings = list(pairs(members))

    # if odd number of people
    if len(pairings[-1]) == 1:
        pairings[-2] += pairings[-1]
        del pairings[-1]

    for pair in pairings:
        result = Client.api_call(method='conversations.open',
                        users=','.join(pair))

        im_id = result['channel']['id']

        with open("events/strings.json") as f:
            all_strings = json.load(f)

        Client.api_call(method='chat.postMessage',
                        channel=im_id,
                        text=all_strings['pair_welcome'])
