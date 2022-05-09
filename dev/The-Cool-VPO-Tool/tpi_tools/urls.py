from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^tpi_page/$', views.tpi_page, name='tpi_page'),
    url(r'^$', views.tps_in_db, name='tps'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^about/$', views.about, name='about'),
    ####################################################################################################################
    url(r'^tp_bin2bin/(\S{24})/(.*)', views.show_b2b, name='show_b2b'),
    url(r'^tp_bin2bin/(\S{26})/(.*)', views.show_b2b, name='show_b2b'),
    url(r'^tp_bin2bin/(\S{45})/(.*)', views.show_b2b, name='show_b2b'),
    url(r'^tp_bin2bin/(\S{46})/(.*)', views.show_b2b, name='show_b2b'),
    url(r'^tp_bin2bin/(\S{47})/(.*)', views.show_b2b, name='show_b2b'),
    ####################################################################################################################
    url(r'^tp_vid/(\S{24})/(\w{13})/', views.vid, name='vid'),
    url(r'^tp_vid/(\S{24})/(\w{17})/', views.vid, name='vid'),
    url(r'^tp_vid/(\S{26})/(\S{18})/', views.vid, name='vid'),
    url(r'^tp_vid/(\S{45})/(\S{13})/', views.vid, name='vid'),
    url(r'^tp_vid/(\S{46})/(\S{13})/', views.vid, name='vid'),
    url(r'^tp_vid/(\S{47})/(\S{13})/', views.vid, name='vid'),
    ####################################################################################################################
    url(r'^save_b2b/(\S{24})/', views.save_b2b, name='save_b2b'),
    url(r'^save_b2b/(\S{45})/', views.save_b2b, name='save_b2b'),
    url(r'^save_b2b/(\S{46})/', views.save_b2b, name='save_b2b'),
    url(r'^save_b2b/(\S{47})/', views.save_b2b, name='save_b2b'),
    ####################################################################################################################
    url(r'^save_b2b_explanation_only/(\S{24})/', views.save_b2b_only_explanations, name='save_b2b_explanation_only'),
    url(r'^save_b2b_explanation_only/(\S{45})/', views.save_b2b_only_explanations, name='save_b2b_explanation_only'),
    url(r'^save_b2b_explanation_only/(\S{46})/', views.save_b2b_only_explanations, name='save_b2b_explanation_only'),
    url(r'^save_b2b_explanation_only/(\S{47})/', views.save_b2b_only_explanations, name='save_b2b_explanation_only'),
    ####################################################################################################################

    url(r'^tp_bin2bin/submit_explanations/', views.submit_explanations, name='submit_explanations'),

    #url(r'^tp_bin2bin/submit_explanations/', views.submit_explanations, name='submit_explanations'),

    ]
