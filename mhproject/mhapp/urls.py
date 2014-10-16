from django.conf.urls import patterns, include, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView, TemplateView
from clubs import views

urlpatterns = patterns('',
	url(r'^register/$', views.register , name='register_user'),
)