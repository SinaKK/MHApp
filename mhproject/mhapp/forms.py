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
	def clean_username(self):
		un = self.cleaned_data['username']
		try:
			User.objects.get(username__iexact=un)
			raise forms.ValidationError("Username is already in use.")
		except User.DoesNotExist:
			pass
		return un
		
	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			User.objects.get(email__iexact=email)
			raise forms.ValidationError("Email is already in use.")
		except User.DoesNotExist:
			pass
		return email

			

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

	def __init__(self, *args, **kwargs):
		self.user = kwargs['instance']
		super(EditUserForm,self).__init__(*args,**kwargs)
		
	def clean_email(self):
		email = self.cleaned_data['email']
		if self.user.email == email:
			return email
		try:
			User.objects.get(email__iexact=email)
			raise forms.ValidationError("Email is already in use.")
		except User.DoesNotExist:
			pass
		return email



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
