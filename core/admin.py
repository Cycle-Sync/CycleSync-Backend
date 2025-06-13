from django.contrib import admin
from django.urls import path
from django.contrib.auth.models import User
from .models import *
admin.site.register(Profile)
admin.site.register(Cycle)
admin.site.register(DailyEntry)
@admin.register(Condition)
class ConditionAdmin(admin.ModelAdmin):
    list_display = ('name',)


