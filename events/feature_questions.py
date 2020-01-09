from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient
import datetime

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings,
'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)

def test(request):
    slack_message = request.data

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

            from apscheduler.schedulers.background import BackgroundScheduler

            from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

            scheduler = BackgroundScheduler()
            # TODO - adding this causes the jobs to be run multiple times
            #scheduler.add_jobstore(DjangoJobStore(), "default")
            from events.text_user import send_prof_dev_info

            print("Adding jobs...")
            next_date = datetime.datetime.now()
            for i in range(2):
                scheduler.add_job(send_prof_dev_info, 'date', run_date=next_date, args=[user])
                next_date += datetime.timedelta(seconds=10)
            scheduler.start()
            print("Scheduler started!")
            
            #Client.api_call(method='chat.postMessage',
            #                channel=channel,
            #                text=bot_text)
            return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_200_OK)
