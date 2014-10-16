from django import forms
from mhapp.models import *
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _


class MyRegistrationForm(UserCreationForm):
	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2')

class ProfileForm(ModelForm):
	class Meta:
		model = Profile
		labels = {
            'notify': _('Enable Email Reminders'),
        }
		exclude = ['user']

class EditUserForm(ModelForm):
	class Meta:
		model = User
		fields = ('email',)



class EditProfileForm(ModelForm):
	class Meta:
		model = Profile
		exclude = ['user']
		labels = {
						'notify': _('Enable Email Reminders'),
				}

class ReportTypeForm(ModelForm):
    class Meta:
        model = ReportType


QuestionFormSet = inlineformset_factory(ReportType, Question)
