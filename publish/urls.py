# coding:utf-8
from django.conf.urls import patterns, include, url
from publish.views import *

urlpatterns = patterns('',
                       url(r'^project/init/list/$', initProject, name='initProject'),
                       url(r'^project/init/create/$', createProject, name='createProject'),
                       url(r'^project/init/delete/$', projectDelete, name='projectDelete'),

                       url(r'^project/level/list/$', LevelList, name='LevelList'),
                       url(r'^project/level/create/$', LevelCreate, name='LevelCreate'),
                       url(r'^project/level/delete/$', LevelDelete, name='LevelDelete'),
                       url(r'^project/level/detail/$', LevelDetail, name='LevelDetail'),

                       url(r'^project/template/list/$', templateList, name='templateList'),
                       url(r'^project/template/checkboxlist/$', templateCheckboxList, name='templateCheckboxList'),
                       url(r'^project/template/create/$', templateCreate, name='templateCreate'),
                       url(r'^project/template/delete/$', templateDelete, name='templateDelete'),

                       url(r'^publishsheet/create/$', createPublishSheet, name='createPublishSheet'),
                       url(r'^publishsheet/delete/$', PublishSheetDelete, name='PublishSheetList'),
                       url(r'^publishsheet/list/$', PublishSheetList, name='PublishSheetList'),
                       url(r'^publishsheet/list/done/$', PublishSheetDoneList, name='PublishSheetDoneList'),
                       url(r'^publishsheet/reason/$', PublishSheetRefuseReason, name='PublishSheetRefuseReason'),
                       url(r'^publishsheet/detail/$', PublishSheetDetail, name='PublishSheetDetail'),
                       url(r'^publishsheet/publish/start/$', StartPublish, name='StartPublish'),

                       url(r'^approve/list/$', ApproveList, name='ApproveList'),
                       url(r'^approve/init/$', ApproveInit, name='ApproveInit'),  # 单个审批单
                       url(r'^approve/judge/$', ApproveJudge, name='ApproveJudge'),
                       )
