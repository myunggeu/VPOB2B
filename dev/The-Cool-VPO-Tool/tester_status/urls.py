from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from tester_status import views

urlpatterns = [
    url(r'^$', views.tester_status, name='tester_status'),
    url(r'^add_testers/$', views.add_testers, name='add_testers'),
    url(r'^update/', views.tester_up_down, name='tester_down'),
    ]
