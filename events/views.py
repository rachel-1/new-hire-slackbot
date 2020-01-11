from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

from events.event_processing import process_event
import datetime

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)

class Events(APIView):
    def __init__(self):
        super(Events).__init__()
        self.scheduler = BackgroundScheduler(
        {'apscheduler.executors.default': {
            'type': 'threadpool',
            'max_workers': '1'}
        })
        # TODO - has bug similar to https://github.com/agronholm/apscheduler/issues/305 (though it seems to create a bunch of duplicates instead)
        #self.scheduler.add_jobstore(DjangoJobStore(), "default")
        self.scheduler.start()

    def post(self, request, *args, **kwargs):
        print("request.data: ", request.data) # TODO - remove debug statement
        if False:
            from events.models import User
            from datetime import date
            user1 = User(username="rachel0",
                         slack_user_id="URY87UWUS",
                         slack_team_id="",
                         real_name="Rachel Gardner",
                         bot_dm_id="",
                         manager_id="",
                         manager_name="",
                         prof_dev_channel="GSGG2KC7J",
                         manager_prof_dev_channel="GSJNAFJNS",
                         progress_channel="GSGHZMKG8",
                         questions_channel="CS0908BAP",
                         greet_stage=0,
                         prof_dev_stage=0,
                         join_date=date.today())
            user1.save()

        slack_message = request.data

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Verification challenge
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)

        # ignore messages from the bot
        if slack_message['event'].get('subtype') == 'bot_message':
            return Response(status=status.HTTP_200_OK)

        self.scheduler.add_job(process_event, 'date',
                               run_date=datetime.datetime.now(),
                               args=[self.scheduler, slack_message])
        
        return Response(status=status.HTTP_200_OK)
