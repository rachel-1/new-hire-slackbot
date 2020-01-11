import time
from rest_framework.response import Response
from rest_framework import status
from events.models import User
from events.feature_greet import send_greeting_message, get_manager
import datetime

def process_event(scheduler, slack_message):
    event = slack_message['event']
    if event['type'] == 'team_join':
        send_greeting_message(event)
    elif event['type'] == 'message':
        user_id = event['user']
        user = User.objects.get(slack_user_id=user_id)
        if event['channel'] == user.bot_dm_id:
            get_manager(event)
        if event['channel'] == user.progress_channel:
            from events.progress_features import progress_channel_handler
            progress_channel_handler(scheduler, user, slack_message)

        elif event['channel'] == user.prof_dev_channel:
            # TODO - should happen when person first joins

            import events.prof_dev_features as prof_dev_features
            prof_dev_features.get_goals(user_id)
            prof_dev_features.setup_articles(scheduler, user_id)
            time.sleep(5)
            prof_dev_features.remind_about_goals(user_id)
            #pass # no data is read from the user right now

        elif event['channel'] == user.questions_channel:
            pass
            # TODO - this scheduler has no visibility into what else has been scheduled
            '''
            from events.question_features import qs_reminder
            jobs = scheduler.get_jobs()
            if 'q_reminder' in jobs:
                scheduler.remove_job('q_reminder')
            next_time = datetime.datetime.now() + datetime.timedelta(seconds=10)
            scheduler.add_job(qs_reminder, 'date',
                              run_date=next_time+datetime.timedelta(seconds=10),
                              args=[user_id], id='q_reminder')
            '''
 
