from django.test import TestCase
from django.core.urlresolvers import reverse
from datetime import date

# Create your tests here.
from mhapp.models import *


def setUp(self):
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
  user = User.objects.create_user(username="mhapp", password="mhapp")
  user.is_superuser=1
  user.save()
  user.profile = Profile(user=user)
  user.profile.save()
  user.save()

def create_and_login_user(self):
  user = User.objects.create_user(username="test", password="test")
  user.is_superuser = 0
  user.save()
  user.profile = Profile(user=user)
  user.profile.save()
  user.save()
  self.logged_in = self.client.login(username="test", password="test")
  return user

### Aim: test whether access is correctly limited based on whether user is logged in and whether or not they ar admin
class AuthenticationAccessTest(TestCase):
  def test_home_as_public(self):
    setUp(self)
    response = self.client.get(reverse('home'))
    self.assertContains(response, "You must be logged in to access this site.")
  def test_report_as_public(self):
    setUp(self)
    response = self.client.get(reverse('report',args=(13,)))
    self.assertEqual(response.status_code, 302)
  def test_progress_as_public(self):
    setUp(self)
    response = self.client.get(reverse('progress'))
    self.assertEqual(response.status_code, 302)
  def test_profile_as_public(self):
    setUp(self)
    response = self.client.get(reverse('edit_user'))
    self.assertEqual(response.status_code, 302)
  def test_home_as_user(self):
    setUp(self)
    u = create_and_login_user(self)
    response = self.client.get(reverse('home'))
    self.assertContains(response, "Pending Report")
  def test_report_as_user(self):
    setUp(self)
    u = create_and_login_user(self)
    response = self.client.get(reverse('report',args=(13,)))
    self.assertContains(response, "WHO-5 Report")
  def test_profile_as_user(self):
    setUp(self)
    u = create_and_login_user(self)
    response = self.client.get(reverse('edit_user'))
    self.assertContains(response, "Edit Profile")
  def test_progress_as_user(self):
    setUp(self)
    u = create_and_login_user(self)
    response = self.client.get(reverse('progress'))
    self.assertContains(response, "Your Progress Page")
  def test_admin_panel_as_user(self):
    setUp(self)
    u = create_and_login_user(self)
    response = self.client.get(reverse('app_settings'))
    self.assertEqual(response.status_code, 302)
  def test_admin_panel_as_admin(self):
    setUp(self)
    self.logged_in = self.client.login(username="mhapp", password="mhapp")
    response = self.client.get(reverse('app_settings'))
    self.assertContains(response, "App Settings")



### Tests on Progress Page, if correct output is produced based on data available
class ProgressTest(TestCase):
  def test_progress_no_reports(self):
    setUp(self)
    u = create_and_login_user(self)
    response = self.client.get(reverse('progress'))
    self.assertContains(response, "You have not made any reports!")
  def test_progress_with_reports(self):
    setUp(self)
    u = create_and_login_user(self)
    Report(user=u,type=ReportType.objects.get(id=13),date_created=date.today()).save()
    response = self.client.get(reverse('progress'))
    self.assertNotContains(response, "You have not made any reports!")


### Tests whether delete user feature works and if all user data is removed
class DeleteUserTest(TestCase):
  def test_delete_user(self):
    setUp(self)
    u = create_and_login_user(self)
    Report(user=u,type=ReportType.objects.get(id=13),date_created=date.today()).save()
    self.assertTrue(User.objects.filter(id=u.id).exists())
    self.assertTrue(Report.objects.filter(user=u).exists())
    response = self.client.get(reverse('delete_user'))
    self.assertFalse(User.objects.filter(id=u.id).exists())
    self.assertFalse(Report.objects.filter(user=u).exists())


### Tests Report System, appropiate error messages
class ReportTest(TestCase):
  def test_already_submitted_today(self):
    setUp(self)
    u = create_and_login_user(self)
    Report(user=u,type=ReportType.objects.get(id=13),date_created=date.today()).save()
    response = self.client.get(reverse('report',args=(13,)))
    self.assertContains(response, "You have already completed a ")
