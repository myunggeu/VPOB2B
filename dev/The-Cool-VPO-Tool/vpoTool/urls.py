from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from checker import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^valid_plan/([Ss]\S{3})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{4})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{5})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{6})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{7})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{8})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{9})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{10})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{11})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{12})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{13})/$', views.valid_plan, name='valid_plan'),
    url(r'^valid_plan/([Ss]\S{14})/$', views.valid_plan, name='valid_plan'),


    url(r'^valid_plan/refresh/$', views.refresh_plan, name='refresh_plan'),
    url(r'^valid_plan/delete/$', views.delete_vpo, name='delete_vpo'),
    url(r'^Add_Template/$', views.add_template, name='add_template'),
    url(r'^val_plan_admin/$', views.create_template, name='create_template'),
    url(r'^val_plan_admin_add/$', views.add_to_template, name='add_to_template'),
    url(r'^save_template/$', views.save_template, name='save_template'),
    url(r'^update_vpo/$', views.update_vpo, name='update_vpo'),
    url(r'^update_vpo_info/$', views.update_vpo_info, name='update_vpo_info'),
    url(r'^delete_all_entries/$', views.delete_all_entries, name='delete_all_entries'),
    url(r'^valid_plan/update_valplan_status/$', views.update_valplan_status, name='update_valplan_status'),
    url(r'^save_to_csv/(\S+)/', views.save_csv, name='save_b2b'),
    url(r'^test_time/$', views.test_time, name='test_time'),
    url(r'^update_test_time/$', views.update_test_time, name='update_test_time'),
    url(r'^tester_status/', include('tester_status.urls')),
    url(r'^bin2bin/', include('tpi_tools.urls')),
]

