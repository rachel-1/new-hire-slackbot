from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ['slack_user_id', 'slack_team_id']

admin.site.register(User, UserAdmin)
