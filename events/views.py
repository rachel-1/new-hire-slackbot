from events.feature_questions import create_questions

from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient

class Events(APIView):
    def post(self, request, *args, **kwargs):

        ''' TODO
        from events.models import User
        from datetime import date
        user1 = User(username="rachel0", join_date=date.today())  # create a ToDoList 
        user1.save()  # saves the ToDoList in the database

        print(user1.id)  # prints 1, each list is given an id automatically
        print(User.objects.all())  # prints all of the ToDoLists in the database
        '''
        return create_questions(request)
