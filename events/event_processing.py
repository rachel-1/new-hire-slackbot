from rest_framework.response import Response
from rest_framework import status
from events.models import User

def process_event(scheduler, slack_message):
    print("slack_message: ", slack_message) # TODO - remove debug statement
    event = slack_message['event']
    
    if event['type'] == 'team_join':
        pass
    elif event['type'] == 'message':
        user_id = event['user']
        user = User.objects.get(slack_user_id=user_id)

        if event['channel'] == user.progress_channel:
            from progress_features import progress_channel_handler
            progress_channel_handler(user, slack_message)

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
