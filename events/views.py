from events.feature_questions import create_questions

from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from slackclient import SlackClient

class Events(APIView):
    def post(self, request, *args, **kwargs):
        create_questions(request)
