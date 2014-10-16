from django.test import TestCase
from django.core.urlresolvers import reverse
from datetime import date
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mhproject.settings")
django.setup()

# Create your tests here.
from mhapp.models import *

TextContent(id=1,name="Home Page Welcome",text="""<p> This application is designed for patients to keep track of their health status. This is simply a tool for patients and should not be a replacement for professional treatment.</br></br>

All data in the system is treated anonymously and information will never be shared unless requested. This is not an actively monitored system.</br></br>

Two different medically recognised scales are used to assist patients, namely, DI-5 (Daily Index) and WHO-5 (World Health Organisation).</br></br>

Patients are to answer questions to these reports every day, the system will store this information, and patients are able to see their results and treatment progress graphically.</br></br>
</p> """).save()
TextContent(id=2,name="Progress Page Description",text="""<h4>Legend</h4>
<br>
<strong>Deteriorating: </strong>
<br>Your health is decreasing dangerously.
<br>
<strong>Potential for Change: </strong>
<br>You are in a state where improvements can be made.
<br>
<strong>Improving: </strong>
<br>Your health is currently on track to be healthy.
<br>
<strong>Healthy: </strong>
<br>You are currently in a healthy state!""").save()
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
user = User.objects.create_user(username="mhapp", password="mhapp")
user.is_superuser=1
user.save()
user.profile = Profile(user=user)
user.profile.save()
user.save()
