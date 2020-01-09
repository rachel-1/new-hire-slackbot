from django.db import models

class User(models.Model):
    slack_user_id = models.CharField(max_length=50)
    slack_team_id = models.CharField(max_length=50)
    username = models.CharField(max_length=300)
    real_name = models.CharField(max_length=300)
    join_date = models.DateTimeField()
    bot_dm_id = models.CharField(max_length=50)
    manager_id = models.CharField(max_length=50)
    manager_name = models.CharField(max_length=300)
    greet_stage = models.PositiveSmallIntegerField()
    prof_dev_stage = models.PositiveSmallIntegerField()
    #prof_dev_channel = models.CharField(max_length=50)

class Question(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    post_date = models.DateTimeField()

    def __str__(self):
        return self.text

class Answer(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    question_id = models.ForeignKey('Question', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    post_date = models.DateTimeField()

    def __str__(self):
        return self.text
