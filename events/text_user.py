import json
from events.models import User

def send_prof_dev_info(user_id):
    print("user_id: ", user_id) # TODO - remove debug statement
    user = User.objects.get(slack_user_id=user_id)
    print("user: ", user) # TODO - remove debug statement

    index = "0"
    
    with open("events/strings.json") as f:
        all_strings = json.load(f)
        info = all_strings['professional_development'][index]

    print("info: ", info) # TODO - remove debug statement
