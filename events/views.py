from events.feature_greet import send_greeting_message, get_manager

from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)

class Events(APIView):
    def post(self, request, *args, **kwargs):
        '''
        from events.models import User
        from datetime import date
        user1 = User(username="rachel0",
                     slack_user_id="URY87UWUS",
                     slack_team_id="",
                     real_name="Rachel Gardner",
                     bot_dm_id="",
                     manager_id="",
                     manager_name="",
                     greet_stage=0,
                     prof_dev_stage=0,
                     join_date=date.today())  # create a ToDoList
        user1.save()  # saves the ToDoList in the database

        print(user1.id)  # prints 1, each list is given an id automatically
        print(User.objects.all())  # prints all of the ToDoLists in the database
        '''
        slack_message = request.data
        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)
        # Verification challenge
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message,
                            status=status.HTTP_200_OK)
        #get_manager(request)
        #send_greeting_message(request)
        from events.feature_questions import test
        test(request)
        return Response(status=status.HTTP_200_OK)
