from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.backends import ModelBackend

from datetime import datetime
from django.core.mail import send_mail

from mhproject import settings
#Change your models (in models.py).
#Run python manage.py makemigrations to create migrations for those changes
#Run python manage.py migrate to apply those changes to the database.


class Concern(models.Model):
  text = models.CharField(max_length=200)
  def __str__(self):
        return "%s" % self.text

class Profile(models.Model):
    # User has username, password, first_name, last_ame and email, date_joined
    user = models.OneToOneField(User)  # this class, Profile, extends User by connecting them through this onetoone field

     # so e.g user = User.objects.get(username="sina")
    # profile is not autocreated, so when creating a new user, make a new profile and set the field
    # but you can set the profile like this: user.profile = some_profile
    # or directly user.profile = Profile(twitter="my_twitter")
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Not Assigned'),
    )

    gender =  models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')
    age =  models.IntegerField(max_length=150, blank=True, null=True)

    notify = models.BooleanField(default=False)

    concern = models.ForeignKey(Concern,blank=True,null=True)

    def __str__(self):
          return "%s's profile" % self.user




class CaseInsensitiveModelBackend(ModelBackend):
  """
  By default ModelBackend does case _sensitive_ username authentication, which isn't what is
  generally expected.  This backend supports case insensitive username authentication.
  """
  def authenticate(self, username=None, password=None):
    try:
      user = User.objects.get(username__iexact=username)
      if user.check_password(password):
        return user
      else:
        return None
    except User.DoesNotExist:
      return None


class ReportType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Report(models.Model):
	date_created = models.DateField()
	user = models.ForeignKey(User)
	type = models.ForeignKey(ReportType)



class Question(models.Model):
    type = models.ForeignKey(ReportType)
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text

class Answer(models.Model):
	report = models.ForeignKey(Report)
	question = models.ForeignKey(Question)
	score = models.IntegerField(max_length=10)

class QuestionTrigger(models.Model):
    CHECKS = (
        ('<','<'),
        ('>','>')
    )

    question = models.ForeignKey(Question)
    threshold = models.IntegerField(max_length=10,default=-1)
    type = models.CharField(max_length=1, choices=CHECKS,default='<')
    description = models.TextField()

class ReportTrigger(models.Model):
    CHECKS = (
        ('<','<'),
        ('>','>')
    )

    reportType = models.ForeignKey(ReportType)
    threshold = models.IntegerField(max_length=10,default=-1)
    type = models.CharField(max_length=1, choices=CHECKS,default='<')
    description = models.TextField()

class Constants(models.Model):
	name = models.CharField(max_length=150)
	value = models.FloatField()

class TextContent(models.Model):
  name = models.CharField(max_length=150)
  text = models.TextField()


class TempURL(models.Model):
	created = models.DateTimeField()
	url = models.CharField(max_length=32)
	user = models.OneToOneField(User)
	def save(self, *args, **kwargs):
		self.created = datetime.now(timezone.utc)
		return super(TempURL, self).save(*args, **kwargs)
