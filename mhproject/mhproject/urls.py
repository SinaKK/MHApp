from django.conf.urls import patterns, include, url
from django.contrib import admin
from mhapp import views
from django.views.generic import CreateView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mhproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    ### ALL USERS
    #Home
    url(r'^$', views.home, name='home'),

    #Report
    url(r'^report/(?P<type>\d+)/$', views.report, name='report'),
    url(r'^report/(?P<type>\d+)/submit$', views.report_submit, name='report_submit'),
    url(r'^report/success$', views.report_success, name='report_success'),

    #Progress
    url(r'^progress/$', views.progressview, name='progress'),

    #Export - user
    url(r'^export/user$', views.user_export, name='user_export'),

    #User/Authentication
    url(r'^register/$', views.register , name='register_user'),
    url(r'^login/$', views.custom_login, {'template_name': 'login.html',}, name='login'),
    url(r'^unauth/$', views.unauth, {'template_name': 'login.html',}, name='unauth'),
    url(r'^logout/$', 'django.contrib.auth.views.logout' ,{'next_page': '/#'}, name='logout'),
    url(r'^profile/edit/$', views.edit_user, name='edit_user'),
    url(r'^profile/$', views.show_user, name='show_user'),
    url(r'^password/change$', 'django.contrib.auth.views.password_change', {'template_name': 'password_change.html'}, name='password_change'),
    url(r'^password/change/done/$', 'django.contrib.auth.views.password_change_done', {'template_name': 'password_change_done.html'}, name='password_change_done'),
    url(r'^password/reset/$', 'django.contrib.auth.views.password_reset', {'template_name': 'password_reset.html'}, name='password_reset'),
    url(r'^password/reset/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name': 'password_reset_done.html'}, name='password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name': 'password_reset_confirm.html'}, name='password_reset_confirm'),
    url(r'^password/reset/complete/$', 'django.contrib.auth.views.password_reset_complete', {'template_name': 'password_reset_complete.html'}, name='password_reset_complete'),

    #|-Delete User
    url(r'^delete_user/$', views.delete_user, name='delete_user'),

    ###ADMIN ONLY###
    #Django built in admin (not used)
    url(r'^admin/$', include(admin.site.urls)),

    #Main Admin Control Panel
    url(r'^manage/settings/$', views.app_settings,name='app_settings'),

    #Backup System
    url(r'^backups/$', views.backups, name='backups'),
    url(r'^backups/backup/$', views.backup, name='backups_backup'),
    url(r'^backups/restore/(?P<filename>[\w.]+)/$', views.restore, name='backups_restore'),
    url(r'^backups/delete/(?P<filename>[\w.]+)/$', views.delete, name='backups_delete'),
    url(r'^backups/download/(?P<filename>[\w.]+)/$', views.download, name='backups_download'),

    #Report Management
    url(r'^manage/report/(?P<pk>\d+)/edit/$', views.ReportTypeUpdateView.as_view(),name='manage_report_edit'),
    url(r'^manage/report/(?P<pk>\d+)/delete/$', views.ReportTypeDeleteView.as_view(),name='manage_report_delete'),
    url(r'^manage/report/new$', views.ReportTypeCreateView.as_view(),name='manage_report_new'),

    url(r'^manage/text/(?P<pk>\d+)/edit/$', views.TextContentUpdateView.as_view(),name='manage_text_content'),

    #Constant Management
    url(r'^manage/restore/$', views.restore_to_default,name='restore_to_default'),

    #Constant Management
    url(r'^manage/constants/$', views.manage_constants,name='manage_constants'),

    #Concerns Management
    url(r'^manage/concerns/$', views.manage_concerns,name='manage_concerns'),

    #alerts management
    url(r'^manage/alerts/$', views.manage_alerts,name='manage_alerts'),

	  #Export - Aggregate
    url(r'^export/all$',views.admin_export, name='admin_export'),


	url(r'^email_sent/$', views.email_sent, name='email_sent'),
	url(r'^share/(?P<temp>[\w.]+)/$', views.share_data, name='share_data'),

)
