
def create_new_hire_channel():
    self.scheduler.add_job(create_new_hire_channel, 'date',
                           run_date=datetime.datetime.now() + datetime.timedelta(days=1),
                           args=[self.scheduler, slack_message])
   
