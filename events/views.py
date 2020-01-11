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
        self.scheduler.start()

    def post(self, request, *args, **kwargs):
        # print("request: ", request.META) # TODO - remove debug statement
        print("IN POST")
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
        if slack_message['event'].get('subtype') == 'bot_message' or \
            'bot_profile' in slack_message['event']:
            print("DETECTED IS A BOT")
            return Response(status=status.HTTP_200_OK)

        self.scheduler.add_job(process_event, 'date',
                               run_date=datetime.datetime.now(),
                               args=[self.scheduler, slack_message])
        return Response(status=status.HTTP_200_OK)
