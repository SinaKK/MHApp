from django.core.management.base import BaseCommand, CommandError
from datetime import date
from django.core.mail import send_mail
from mhapp.models import *


class Command(BaseCommand):
    args = ''
    help = 'Sends email reminders'

    def handle(self, *args, **options):
        users = User.objects.filter(profile__notify = True)
        for user in users:
            if not Report.objects.filter(user=user,date_created=date.today()).exists():
                send_mail('Mental Health Thermometer - Email Reminder', 'Hello ' + user.username + ',\n\nThis is a friendly reminder that you have pending reports on the Mental Health Thermometer.\n\nRegards,\n\nMental Health Thermometer Team\n\n (You can disable email reminders via Edit Profile)',settings.EMAIL_HOST_USER,[user.email],fail_silently=False)
