# coding:utf-8
from django.conf.urls import patterns, include, url
from publish.views import *

urlpatterns = patterns('',
                       url(r'^initProject/$', initProject, name='initProject'),
                       url(r'^createProject/$', createProject, name='createProject'),
                       )
