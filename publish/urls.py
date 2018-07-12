# coding:utf-8
from django.conf.urls import patterns, include, url
from publish.views import *

urlpatterns = patterns('',
                       url(r'^initProject/$', initProject, name='initProject'),
                       url(r'^createProject/$', createProject, name='createProject'),
                       url(r'^publishsheet/create/$', createPublishSheet, name='createPublishSheet'),
                       url(r'^publishsheet/list/$', PublishSheetList, name='PublishSheetList'),
                       url(r'^approve/list/$', ApproveList, name='ApproveList'),
                       )
