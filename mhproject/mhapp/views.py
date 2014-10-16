import os
import csv
import time
import json
import shutil
import math

import datetime
from time import mktime, time
import time

from os import listdir
from os.path import isfile, join, exists, splitext, basename

from operator import itemgetter

from collections import Counter,defaultdict

from mhapp.forms import *
import mhapp.models

from django.shortcuts import render, redirect, get_object_or_404

import django.contrib.auth.backends
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import login
from django.contrib.auth.decorators import login_required,user_passes_test

from django.utils.dateparse import *
from django.views.generic.detail import DetailView
from django.views.generic import CreateView,UpdateView,DeleteView

from django.forms.models import modelformset_factory,inlineformset_factory

from django.utils.decorators import method_decorator
from django.utils import timezone

from django.http import HttpResponseRedirect, HttpResponse

from django.core import management

from django.core.urlresolvers import reverse_lazy, reverse

from django.core.mail import send_mass_mail

from django.core.exceptions import *


import uuid
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.

# Home Page



def home(request):
  pending_reports = []
  alldone = True
  context = {}
  if request.user.is_authenticated():
    types = ReportType.objects.all()

    for t in types:
      r = Report.objects.filter(user=request.user, type=t)
      if r:
        r = r.latest('date_created')
        if r.date_created < datetime.date.today():
          t.done = False
          alldone = False
        else:
          t.done = True
        pending_reports.append(t)
      else:
        pending_reports.append(t)
    allreports = Report.objects.filter(user=request.user)
    if allreports:
      latest = allreports.latest('date_created').date_created
    else:
      latest = ""
    num_reports = allreports.count()
    context.update({'latest':latest,'num_reports':num_reports})

  context.update({'pending_reports': pending_reports,'all_reports_done':alldone,'welcome_content':TextContent.objects.get(name="Home Page Welcome").text}) # setup context

  # render page with html template and context
  return render(request, 'mhapp/index.html', context)

def types(request):
  """Used by settings.TEMPLATE_CONTEXT_PROCESSORS to give all report types to every template"""
  types = ReportType.objects.all()
  return {'types': types}

@login_required
def report(request,type):
  type =  get_object_or_404(ReportType,id=type)
  context = {}
  if request.GET.get('old'):
    context.update({'old':1})
  completed = 0
  r = Report.objects.filter(user=request.user, type=type)
  if r:
    r = r.latest('date_created')
    if r.date_created == datetime.date.today() and not request.GET.get('old'):
      completed = 1

  questions = Question.objects.filter(type=type)
  session = Report.objects.filter(user=request.user,type=type).count() + 1
  for i,q in enumerate(questions):
    if i > 0:
      questions[i-1].next = questions[i].id
  context.update( {'type': type,'questions':questions,'date':datetime.date.today(),'session':session,'completed': completed})

  if request.GET.get('error'):
    error = request.GET['error']
    context.update({"error": str(error) })
  return render(request,'mhapp/report.html', context)


@login_required
def report_submit(request,type):
  type =  get_object_or_404(ReportType,id=type)
  questions = Question.objects.filter(type=type)
  alerts = []

  for q in questions:
    key = "answer_" + str(q.id)
    if key not in request.POST:
      return redirect(reverse('report', kwargs={'type': type.id})+"?old=1&error=1")
  if "olddate" in request.POST:
    print("old")
    date = request.POST['olddate']
    date = parse_date(date)

    print(date)
    if (not date) or Report.objects.filter(user=request.user,type=type,date_created=date).exists():
      return redirect(reverse('report', kwargs={'type': type.id})+"?old=1&error=2")
    r = Report(user=request.user, type=type,date_created=date)
    print(r.date_created)
    r.save()
    print(r.date_created)
  else:
    print("new")
    if Report.objects.filter(user=request.user,type=type,date_created=datetime.date.today()).exists():
      return redirect(reverse('report', kwargs={'type': type.id})+"?error=2")
    r = Report(user=request.user, type=type,date_created=datetime.date.today())
    r.save()

  #Start of Alerts Check (Trigger System), Checks based on Alerts set up in App Settings
  total = 0
  for q in questions:
    key = "answer_" + str(q.id)
    s = request.POST[key]
    total += int(s)
    a = Answer(report=r,question=q,score=s)
    a.save()

    #Question Threshold Check
    try:
        qcheck = QuestionTrigger.objects.filter(question=q)
        for eachq in qcheck:
            if(eachq.type == '<'):
                if(int(s) < eachq.threshold):
                    alerts.append(eachq.description)
            else:
                if(int(s) > eachq.threshold):
                    alerts.append(eachq.description)
    except ObjectDoesNotExist:
        print("noalerts")

  #Report Threshold Check
  types = ReportType.objects.all()
  for eachtype in types:
    try:
        matched = ReportTrigger.objects.filter(reportType=eachtype)
        for eachr in matched:
            if(eachr.type == '<'):
                if(total < eachr.threshold):
                    alerts.append(eachr.description)
            else:
                if(total > eachr.threshold):
                    alerts.append(eachr.description)
    except ObjectDoesNotExist:
        print("noalerts")

  messages.success(request, type.name + ' report submitted successfully!')

  request.session['alerts'] = alerts
  return redirect('report_success')

def report_success(request):
  pending_reports = []
  alldone = True
  context = {}
  if request.user.is_authenticated():
    types = ReportType.objects.all()

    for t in types:
      r = Report.objects.filter(user=request.user, type=t)
      if r:
        r = r.latest('date_created')
        if r.date_created < datetime.date.today():
          t.done = False
          alldone = False
        else:
          t.done = True
        pending_reports.append(t)
      else:
        pending_reports.append(t)
    allreports = Report.objects.filter(user=request.user)
    if allreports:
      latest = allreports.latest('date_created').date_created
    else:
      latest = ""
    num_reports = allreports.count()
    context.update({'latest':latest,'num_reports':num_reports})

  context.update({'pending_reports': pending_reports,'all_reports_done':alldone, 'alerts':request.session['alerts']}) # setup context
  # render page with html template and context
  return render(request, 'mhapp/reportsuccess.html', context)


class ReportTypeCreateView(CreateView):
    template_name = 'mhapp/manage_report.html'
    model = ReportType
    form_class = ReportTypeForm
    success_url = '/'
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        questions_form = QuestionFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(form=form,questions_form=questions_form))
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        questions_form = QuestionFormSet(self.request.POST)

        if (form.is_valid() and questions_form.is_valid()):
            return self.form_valid(form, questions_form)
        else:
            return self.form_invalid(form, questions_form)
    def form_valid(self, form, questions_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        questions_form.instance = self.object
        questions_form.save()
        messages.success(self.request, 'New Report Created.')
        return redirect('app_settings')
    def form_invalid(self, form, questions_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render(
            self.get_context_data(form=form,
                                  questions_form=questions_form,))
    @method_decorator(user_passes_test(lambda u: u.is_superuser,login_url='/unauth/'))
    def dispatch(self, *args, **kwargs):
        return super(ReportTypeCreateView, self).dispatch(*args, **kwargs)


class ReportTypeUpdateView(UpdateView):
    template_name = 'mhapp/manage_report.html'
    model = ReportType
    form_class = ReportTypeForm
    success_url = ''
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        questions_form = QuestionFormSet(instance=self.object)
        return self.render_to_response(self.get_context_data(form=form,questions_form=questions_form))
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance and its inline
        formsets with the passed POST variables and then checking them for
        validity.
        """
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        questions_form = QuestionFormSet(self.request.POST, instance=self.object)

        if (form.is_valid() and questions_form.is_valid()):
            return self.form_valid(form, questions_form)
        else:
            return self.form_invalid(form, questions_form)
    def form_valid(self, form, questions_form):
        """
        Called if all forms are valid. Creates a Recipe instance along with
        associated Ingredients and Instructions and then redirects to a
        success page.
        """
        self.object = form.save()
        questions_form.instance = self.object
        questions_form.save()
        messages.success(self.request, 'Report Updated.')
        return redirect('app_settings')
    def form_invalid(self, form, questions_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render(
            self.get_context_data(form=form,
                                  questions_form=questions_form,))
    @method_decorator(user_passes_test(lambda u: u.is_superuser,login_url='/unauth/'))
    def dispatch(self, *args, **kwargs):
        return super(ReportTypeUpdateView, self).dispatch(*args, **kwargs)

class ReportTypeDeleteView(DeleteView):
    model = ReportType
    success_url = reverse_lazy('app_settings')
    @method_decorator(user_passes_test(lambda u: u.is_superuser,login_url='/unauth/'))
    def dispatch(self, *args, **kwargs):
        return super(ReportTypeDeleteView, self).dispatch(*args, **kwargs)

class TextContentUpdateView(UpdateView):
    model = TextContent
    fields = ['name','text']
    success_url = reverse_lazy('app_settings')
    @method_decorator(user_passes_test(lambda u: u.is_superuser,login_url='/unauth/'))
    def dispatch(self, *args, **kwargs):
        return super(TextContentUpdateView, self).dispatch(*args, **kwargs)

@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def app_settings(request):
  constants = Constants.objects.all()
  concerns = Concern.objects.all()
  qalerts = QuestionTrigger.objects.all()
  ralerts = ReportTrigger.objects.all()
  textcontents = TextContent.objects.all()
  num_accounts = User.objects.all().count()
  num_reports = Report.objects.all().count()
  return render(request, 'mhapp/app_settings.html', {"constants":constants,"concerns":concerns, "qalerts":qalerts, "ralerts":ralerts,'textcontents':textcontents,'num_accounts':num_accounts,'num_reports':num_reports})

@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def manage_constants(request):
  ConstantsFormSet = modelformset_factory(Constants)
  if request.method == 'POST':
        formset = ConstantsFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Constants Updated.')
            return redirect('app_settings')
            # do something.
  else:
      formset = ConstantsFormSet()
  return render(request, 'mhapp/manage_constants.html', {"formset":formset})

@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def manage_concerns(request):
  ConcernsFormSet = modelformset_factory(Concern)
  if request.method == 'POST':
        formset = ConcernsFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Concerns Updated.')
            return redirect('app_settings')
            # do something.
  else:
      formset = ConcernsFormSet()
  return render(request, 'mhapp/manage_concerns.html', {"formset":formset})



@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def restore_to_default(request):
  TextContent.objects.filter(id__gt=2).delete()
  Constants.objects.filter(id__gt=10).delete()
  Concern.objects.filter(id__gt=10).delete()
  TextContent(id=1,name="Home Page Welcome",text="<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec sapien in mi consequat dapibus vulputate a quam. Integer vel enim eget velit consequat iaculis. Vivamus non feugiat leo. Sed ut aliquet risus. Fusce in venenatis odio, ac imperdiet massa. Donec eu efficitur dui. Phasellus dapibus dignissim leo, iaculis placerat massa finibus eget. Ut in lobortis risus, id faucibus lacus. Donec ut sodales erat. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Vivamus interdum ante eleifend posuere egestas. Vestibulum id bibendum tortor, eget ullamcorper odio. Sed finibus, lacus ac sodales imperdiet, augue arcu fermentum lacus, eget lobortis purus enim id purus. Duis rhoncus lectus massa, ut mattis arcu consectetur et. Sed euismod felis mauris, at congue elit porttitor quis. Morbi in urna quam.</p><p>Aenean ut mollis libero. Cras eu pretium erat. Pellentesque nisl leo, porttitor et arcu eu, viverra tempor mi. Fusce in ornare quam, ut condimentum erat. Cras pretium accumsan leo vitae consectetur. Aliquam nec hendrerit nibh. Donec ut tincidunt nisi. Aliquam hendrerit ornare gravida. Nam dapibus id enim et tincidunt. Ut at arcu sem. Sed vel turpis vel massa tempor sagittis. Nullam sed augue et nibh porttitor scelerisque.</p>").save()
  TextContent(id=2,name="Progress Page Description",text="<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec sapien in mi consequat dapibus vulputate a quam. Integer vel enim eget velit consequat iaculis. Vivamus non feugiat leo. Sed ut aliquet risus. Fusce in venenatis odio, ac imperdiet massa. Donec eu efficitur dui. Phasellus dapibus dignissim leo, iaculis placerat massa finibus eget. Ut in lobortis risus, id faucibus lacus. Donec ut sodales erat. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Vivamus interdum ante eleifend posuere egestas. Vestibulum id bibendum tortor, eget ullamcorper odio. Sed finibus, lacus ac sodales imperdiet, augue arcu fermentum lacus, eget lobortis purus enim id purus. Duis rhoncus lectus massa, ut mattis arcu consectetur et. Sed euismod felis mauris, at congue elit porttitor quis. Morbi in urna quam.</p>").save()
  Constants(id=1,name="W_RoM",value=0.89).save()
  Constants(id=2,name="W_SDn",value=5.11).save()
  Constants(id=3,name="W_SDc",value=5.58).save()
  Constants(id=4,name="W_Mn",value=12.95).save()
  Constants(id=5,name="W_Mc",value=8.45).save()
  Constants(id=6,name="D_RoM",value=0.89).save()
  Constants(id=7,name="D_SDn",value=3.85).save()
  Constants(id=8,name="D_SDc",value=5.41).save()
  Constants(id=9,name="D_Mn",value=4.47).save()
  Constants(id=10,name="D_Mc",value=8.56).save()
  Concern(id=1,text="Depression").save()
  Concern(id=2,text="Anxiety").save()
  Concern(id=3,text="Anger").save()
  Concern(id=4,text="Eating").save()
  Concern(id=5,text="Sleep").save()
  Concern(id=6,text="Psychosis or Mania").save()
  Concern(id=7,text="Stress").save()
  Concern(id=8,text="Relationship Difficulties").save()
  Concern(id=9,text="Physical Problems").save()
  Concern(id=10,text="Other").save()

  #WHO5
  r, created = ReportType.objects.get_or_create(id=13, name="WHO-5")
  q, created = Question.objects.get_or_create(id=1,type=r)
  q.text="I have felt cheerful and in good spirits"
  q.save()
  q, created =Question.objects.get_or_create(id=2,type=r)
  q.text="I have felt calm and relaxed"
  q.save()
  q, created =Question.objects.get_or_create(id=3,type=r)
  q.text="I have felt active and vigorous"
  q.save()
  q, created =Question.objects.get_or_create(id=4,type=r)
  q.text="I woke up feeling fresh and rested"
  q.save()
  q, created =Question.objects.get_or_create(id=5,type=r)
  q.text="My daily life has been filled with things that interest me"
  q.save()

  #DI5
  r, created = ReportType.objects.get_or_create(id=14, name="DI-5")
  q, created =Question.objects.get_or_create(id=6,type=r)
  q.text="I have felt anxious"
  q.save()
  q, created =Question.objects.get_or_create(id=7,type=r)
  q.text="I have felt depressed"
  q.save()
  q, created =Question.objects.get_or_create(id=8,type=r)
  q.text="I have felt worthless"
  q.save()
  q, created =Question.objects.get_or_create(id=9,type=r)
  q.text="I have thoughts about killing myself"
  q.save()
  q, created =Question.objects.get_or_create(id=10,type=r)
  q.text="I have felt that I am not coping"
  q.save()
  return redirect('app_settings')





@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def manage_alerts(request):
  #Must have prefix as multiple formsets on a page
  QuestionTriggerFormSet = modelformset_factory(QuestionTrigger,can_delete=True)
  ReportTriggerFormSet = modelformset_factory(ReportTrigger,can_delete=True)
  if request.method == 'POST':
        qformset = QuestionTriggerFormSet(request.POST, request.FILES, prefix='q')
        rformset = ReportTriggerFormSet(request.POST, request.FILES, prefix='r')
        if qformset.is_valid() and rformset.is_valid():
            qformset.save()
            rformset.save()
            messages.success(request, 'Alerts Updated.')
            return redirect('app_settings')
            # do something.
  else:
      qformset = QuestionTriggerFormSet(prefix='q')
      rformset = ReportTriggerFormSet(prefix='r')

  return render(request, 'mhapp/manage_alerts.html', {"qformset":qformset, "rformset":rformset})

#User management views below.
#---------------

#Creates User and their Profile. The forms used automatically update with model changes.
def register(request):
  if request.user.is_authenticated():
    messages.success(request, 'You are already registered and logged in as ' + request.user.username + '.')
    return redirect('home')
  elif request.method == 'POST':
    form1 = MyRegistrationForm(request.POST)
    form2 = ProfileForm(request.POST)
    if form1.is_valid() and form2.is_valid():
      new_user = form1.save()
      new_user.save()
      new_profile = form2.save(commit=False)
      new_profile.user = new_user
      new_profile.save()
      new_user.backend = "django.contrib.auth.backends.ModelBackend"
      login(request,new_user)
      messages.success(request, 'New account created! Please login.')
      return redirect('show_user')
  else:
    form1 = MyRegistrationForm()
    form2 = ProfileForm()
  return render(request, "registration.html", {
    'form1': form1, 'form2': form2})


#View to edit certain User and Profile details as specified in EditUserForm and EditProfileForm.
@login_required
def edit_user(request):
  user = request.user
  profile = request.user.profile
  if request.method == 'POST':
    form1 = EditUserForm(request.POST,instance=user)
    form2 = EditProfileForm(request.POST,instance=profile)
    if form1.is_valid() and form2.is_valid():
      edited_user = form1.save()
      edited_profile = form2.save()
      messages.success(request, 'Profile Updated.')
      return redirect('show_user')
  else:
    form1 = EditUserForm(instance=user)
    form2 = EditProfileForm(instance=profile)
  return render(request, "edit_user.html", {
		'form1': form1, 'form2': form2})

#Profile page which shows current logged in User's details. If User/Profile models are changed the template needs to be updated accordingly.
@login_required
def show_user(request):
	user = request.user
	profile = request.user.profile
	return render(request, "show_user.html", {
		'user': user, 'profile': profile})

#Django auth login view modified so a User that is already logged in cannot login again.
def custom_login(request, **kwargs):
	if request.user.is_authenticated():
		messages.success(request, 'You are already logged in as ' + request.user.username + '.')
		return redirect('home')
	else:
		return login(request, **kwargs)
#---------------

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
"""View to set up context for backup page, will return 404 Unauthorized if user is not a superuser."""
@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def backups(request):
  path = os.path.join(BASE_DIR,"backups")
  backups = os.listdir(path)
  context = {'backups': backups}
  return render(request, 'mhapp/backup.html', context)

"""View to append filename by a number until it is unique."""
def unique_filename(filename):
  counter = 1
  fileNameParts = os.path.splitext(filename) # returns ('/path/file', '.ext')
  while os.path.isfile(filename):
    filename = fileNameParts[0] + '_' + str(counter) + fileNameParts[1]
    counter += 1
  return filename

"""View to create a new backup, each new backup name is appended by the current date&time, will also return 404 if Unauthorized"""
@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def backup(request):
  filename = datetime.datetime.now().strftime("backups/backup_%d_%m_%Y_%H_%M.sqlite3")
  if os.path.exists(filename):
    filename = unique_filename(filename)
  shutil.copy(os.path.join(BASE_DIR,"db.sqlite3"), os.path.join(BASE_DIR,filename))
  messages.success(request, 'Backup Created.')
  return redirect("backups")

"""View to restore an existing backup, existing database is removed and backup is moved to root directory
    will return 404 if Unauthorized"""
@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def restore(request,filename):
  filename = os.path.basename(filename)
  path = 'backups/' + filename
  os.remove(os.path.join(BASE_DIR,"db.sqlite3"))
  shutil.copy(os.path.join(BASE_DIR,path), os.path.join(BASE_DIR,"db.sqlite3"))
  messages.success(request, 'Restored to Backup.')
  return redirect("backups")

"""Downloads an existing backup, these should be kept seperately by the administrator to prevent data loss
    returns 404 if Unauthorized"""
@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def download(request,filename):
  filename = os.path.basename(filename)
  path = 'backups/' + filename
  f = open(os.path.join(BASE_DIR,path), 'rb')
  response = HttpResponse(f, content_type='application/x-sqlite3')
  response['Content-Disposition'] = 'attachment; filename=' + filename
  return response

"""Deletes an existing backup from the server, returns 404 if Unauthorized"""
@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def delete(request,filename):
  filename = os.path.basename(filename)
  file = 'backups/' + filename
  os.remove(os.path.join(BASE_DIR,file))
  messages.success(request, 'Backup Deleted!')
  return redirect("backups")

"""Deletes all user information from the database"""
@login_required
def delete_user(request):
  User.objects.get(username=request.user.username).delete()
  messages.success(request, 'Your account and all its data has been removed from the website.')
  return redirect('home')

def get_score(report):
    answers = Answer.objects.filter(report=report)
    score = 0
    for answer in answers:
      score += answer.score
    return score

@login_required
def user_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="my_report.csv"'
    user = request.user
    reports = Report.objects.filter(user=user)
    writer=csv.writer(response)
    writer.writerow([
        'date',
        'score',
        'type',
    ])
    for report in reports:
        writer.writerow([
            report.date_created,
            get_score(report),
            report.type.name,
        ])
    return response


@user_passes_test(lambda u: u.is_superuser,login_url='/unauth/')
def admin_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reports.csv"'
    reports = Report.objects.all()
    writer = csv.writer(response)
    writer.writerow([
        'id',
        'date',
        'total_score',
        'type',
        'gender',
        'age',
        'concern'
    ])
    result=[]
    for report in reports:
        answers = Answer.objects.filter(report=report)
        result=[report.user.id,
            report.date_created,
            get_score(report),
            report.type.name,
            report.user.profile.gender,
            report.user.profile.age,
            ]
        if report.user.profile.concern:
          result.append(report.user.profile.concern)
        else:
          result.append("-")
        for answer in answers:
            result.append(answer.score)
        writer.writerow(result)
    return response

def unauth(request, **kwargs):
  if request.user.is_authenticated():
    messages.success(request, 'You do not have permission to visit that page')
    return redirect('home')
  else:
    return login(request, **kwargs)

#Helper Functions for Equations (As defined in MHT Excel provided by client)

def improvB(report, eq):
    #Calculates Improved Boundary
    score = get_score(report)
    if(score + eq > 10.8):
        return 10.8
    else:
        return eq

def whoDB(report, eq):
    #Calculates Deteriorated Boundary for Who-5
    score = get_score(report)
    if(score - eq > 10.8):
        return (0,10.8)
    elif(score - eq < 1):
        return (0,0)
    else:
        return (0, eq)


def whoPC(eq,ncb,wdb,boundaryimproved):
    #Calculates Potential for Change Boundary for Who-5
    if(wdb + ncb > 25):
        return (wdb,wdb + 0)
    elif(wdb < 0):
        return (wdb,wdb + wdb + 2*eq)
    elif(wdb == 0):
        return (wdb,wdb + boundaryimproved)
    else:
        return (wdb, wdb + ncb)

def whoIB(report,wdb,wpc,ncb,boundaryimproved):
    #Calculates Improved Boundary for Who-5
    if(wdb + wpc > 10.8):
        return (wpc,wpc + 0)
    elif(ncb - boundaryimproved < 0):
        return (wpc, wpc + 0)
    else:
        return (wpc, wpc + ncb - boundaryimproved)

def diIB(ib,ncb,healthy):
    #Calculates Improved Boundary for di-5
    if(ib - ncb < 0):
        return (healthy, 0 + healthy)
    else:
        return (healthy, ib)

def diDB(db, ib,pc):
    #Calculates Deteriorated Boundary for di-5
    if(25 - db <= 0):
        return (25,25)
    else:
        return(pc,25)

@login_required
def progressview(request):
    #Please note that future equations (for future additions of report types) must be added in here.
    alldata = []
    mindate = 0
    types = []
    reported = True

    #Create data (pulls from database), and converts to json (for chart)
    for eachtype in ReportType.objects.all():
        data = []
        types.append(eachtype)
        reports = Report.objects.filter(user=request.user.id).filter(type=eachtype)#TODO: add type
        jsondata = []
        for report in reports:
            tempdict = {'x':-1, 'y':-1}
            score = get_score(report)
            timestamp = time.mktime( report.date_created.timetuple())
            tempdict['x'] = int(timestamp * 1000)
            tempdict['y'] = score
            jsondata.append(tempdict)
        sortedjson = sorted(jsondata, key=itemgetter('x'))
        json.dumps(sortedjson)

        #Calculates Boundaries for each Graph
        try:
            if(eachtype == types[0]):
                #WHO-5
                eq = (1.96*(math.sqrt(2*math.pow(((Constants.objects.get(name="W_SDn").value)*(math.sqrt(1 - Constants.objects.get(name="W_RoM").value))),2))))
                ncb = (Constants.objects.get(name="W_SDn").value * Constants.objects.get(name="W_Mc").value + Constants.objects.get(name="W_SDc").value * Constants.objects.get(name="W_Mn").value)/(Constants.objects.get(name="W_SDn").value + Constants.objects.get(name="W_SDc").value)
                boundaryimproved = improvB(Report.objects.filter(user=request.user.id).filter(type=types[0]).earliest("date_created"),eq)
                db = whoDB(Report.objects.filter(user=request.user.id).filter(type=types[0]).earliest("date_created"),eq)
                pc = whoPC(eq,ncb,db[1],boundaryimproved)
                ib = whoIB(Report.objects.filter(user=request.user.id).filter(type=types[0]).earliest("date_created"),db[1],pc[1],ncb,boundaryimproved)
                healthy = (ib[1],25)
            elif(eachtype == types[1]):
                #DI-5
                ncb = (Constants.objects.get(name="D_SDn").value * Constants.objects.get(name="D_Mc").value + Constants.objects.get(name="D_SDc").value * Constants.objects.get(name="D_Mn").value)/(Constants.objects.get(name="D_SDn").value + Constants.objects.get(name="D_SDc").value)
                healthy = (0,ncb)
                boundaryimproved = get_score(Report.objects.filter(user=request.user.id).filter(type=types[1]).earliest("date_created")) - 1.96*1.805
                boundarydeteriorated = get_score(Report.objects.filter(user=request.user.id).filter(type=types[1]).earliest("date_created")) + 1.96*1.805
                ib = diIB(boundaryimproved,ncb,healthy[1])
                pc = (ib[1],ib[1] + boundarydeteriorated - boundaryimproved)
                db = diDB(boundarydeteriorated,ib[1],pc[1])
            alldata.append((eachtype,sortedjson,db,pc,ib,healthy))
        except ObjectDoesNotExist:
            reported = False

    context = {'user': request.user, 'minD':mindate, 'alldata':alldata, 'reported':reported,'progress_content':TextContent.objects.get(name="Progress Page Description").text}
    return render(request,'mhapp/progresspersonal.html',context)

#User Data Sharing views below.
#------------------------------

#Creates a temporary URL that is associated with the current logged in User. URL is then sent to the User's email.
@login_required
def email_sent(request):
	u = uuid.uuid4() #Random URL
	try:
		TempURL.objects.get(user=request.user).delete() #Delete the previously stored URL so OneToOne model is not violated.
	except TempURL.DoesNotExist:
		pass
	temp_url = TempURL.objects.create(user=request.user,url=u.hex)
	send_mail('Mental Health Thermometer - Your Data', 'Hello,\n\nThe link below can be given to anyone to view your progress:\n\n' + request.build_absolute_uri(reverse('share_data',args=[temp_url.url])) + '\n\nRegards,\n\nThe Mental Health Thermometer Team','Mental Health Thermometer <mentalhealththermometer@gmail.com>', [request.user.email], fail_silently=False)
	messages.success(request, 'You have been sent an email that contains a link that you can share with someone else.')
	return redirect('home')

#Takes a URL of the format specified in urls.py and checks its validity. Displays data if the URL is one associated with a User and it has not expired.
@login_required
def share_data(request,temp):
	try:
		u = TempURL.objects.get(url=temp)
		diff = datetime.datetime.now(timezone.utc) - u.created
		if diff.days > 7: #Current URL expiry is 7 days. Change as needed.
			messages.error(request, 'This link has expired')
			return redirect('home')
		else:
			return progressview_no_login(request,u.user) #Call a modified version of the progress page view that does not require an active user
	except TempURL.DoesNotExist:
		messages.error(request, 'This link is invalid or it has expired')
		return redirect('home')

#Similar to progressview but does not require login. Instances of request.user are replaced by the parameter 'user' that the view receives. Rendered template has been modified as well (has navbar removed for printing).
def progressview_no_login(request,user):
    #Follow same layout as normal progress view
    #Please note that future equations (for future additions of report types) must be added in here.
    alldata = []
    mindate = 0
    types = []
    reported = True

    #Create data (pulls from database), and converts to json (for chart)
    for eachtype in ReportType.objects.all():
        data = []
        types.append(eachtype)
        reports = Report.objects.filter(user=user).filter(type=eachtype)#TODO: add type
        jsondata = []
        for report in reports:
            tempdict = {'x':-1, 'y':-1}
            score = get_score(report)
            timestamp = time.mktime( report.date_created.timetuple())
            tempdict['x'] = int(timestamp * 1000)
            tempdict['y'] = score
            jsondata.append(tempdict)
        sortedjson = sorted(jsondata, key=itemgetter('x'))
        json.dumps(sortedjson)

        #Calculates Boundaries for each Graph
        try:
            if(eachtype == types[0]):
                #WHO-5
                eq = (1.96*(math.sqrt(2*math.pow(((Constants.objects.get(name="W_SDn").value)*(math.sqrt(1 - Constants.objects.get(name="W_RoM").value))),2))))
                ncb = (Constants.objects.get(name="W_SDn").value * Constants.objects.get(name="W_Mc").value + Constants.objects.get(name="W_SDc").value * Constants.objects.get(name="W_Mn").value)/(Constants.objects.get(name="W_SDn").value + Constants.objects.get(name="W_SDc").value)
                boundaryimproved = improvB(Report.objects.filter(user=user).filter(type=types[0]).earliest("date_created"),eq)
                db = whoDB(Report.objects.filter(user=user).filter(type=types[0]).earliest("date_created"),eq)
                pc = whoPC(eq,ncb,db[1],boundaryimproved)
                ib = whoIB(Report.objects.filter(user=user).filter(type=types[0]).earliest("date_created"),db[1],pc[1],ncb,boundaryimproved)
                healthy = (ib[1],25)
            elif(eachtype == types[1]):
                #DI-5
                ncb = (Constants.objects.get(name="D_SDn").value * Constants.objects.get(name="D_Mc").value + Constants.objects.get(name="D_SDc").value * Constants.objects.get(name="D_Mn").value)/(Constants.objects.get(name="D_SDn").value + Constants.objects.get(name="D_SDc").value)
                healthy = (0,ncb)
                boundaryimproved = get_score(Report.objects.filter(user=user).filter(type=types[1]).earliest("date_created")) - 1.96*1.805
                boundarydeteriorated = get_score(Report.objects.filter(user=user).filter(type=types[1]).earliest("date_created")) + 1.96*1.805
                ib = diIB(boundaryimproved,ncb,healthy[1])
                pc = (ib[1],ib[1] + boundarydeteriorated - boundaryimproved)
                db = diDB(boundarydeteriorated,ib[1],pc[1])
            alldata.append((eachtype,sortedjson,db,pc,ib,healthy))
        except ObjectDoesNotExist:
            reported = False

    context = {'minD':mindate, 'alldata':alldata, 'reported':reported,'progress_content':TextContent.objects.get(name="Progress Page Description").text}
    return render(request,'mhapp/progresspersonal_no_login.html',context,)
#------------------------------
