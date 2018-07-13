# coding:utf8
import json
from datetime import datetime
import time

from django.shortcuts import render, HttpResponse, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from publish import models
from asset import models as asset_models
from publish import utils


@login_required
def initProject(request):
    gogroup_objs = asset_models.gogroup.objects.all()
    mailgroup_objs = models.MailGroup.objects.all()
    user_objs = User.objects.all()

    # projectinfo_objs = models.ProjectInfo.objects.all().order_by('group__name')
    projectinfo_dict = {}
    timeslot_objs = models.TimeSlot.objects.all()
    for timeslot in timeslot_objs:
        start_time = ':'.join(timeslot.start_time.split('.')[0].split(':')[:2])
        end_time = ':'.join(timeslot.end_time.split('.')[0].split(':')[:2])
        project_name = timeslot.project_info.group.name
        level_dict = {'start_of_week': timeslot.get_start_of_week_display(), 'end_of_week': timeslot.get_end_of_week_display(),
                      'start_time': start_time, 'end_time': end_time,
                      'approval_level': timeslot.approval_level.get_name_display()}

        if project_name not in projectinfo_dict.keys():
            owner_list = [owner.username for owner in timeslot.project_info.owner.all()]
            mail_group_list = [mail_group.email for mail_group in timeslot.project_info.mail_group.all()]
            projectinfo_dict[project_name] = [owner_list, mail_group_list, level_dict]
        else:
            projectinfo_dict[project_name].append(level_dict)

    project_tuple = sorted(projectinfo_dict.items(), key=lambda d: d[0])
    return render(request, 'publish/gogroup_init.html',
                  {'gogroup_objs': gogroup_objs, 'mailgroup_objs': mailgroup_objs, 'user_objs': user_objs, 'project_tuple': project_tuple})


@login_required
def createProject(request):
    project_name = request.POST['project_name']
    owner_select_list = request.POST.getlist('owner_select_list')
    owner_list = [int(i) for i in owner_select_list]
    first_select_list = request.POST.getlist('first_select_list')
    first_list = [int(i) for i in first_select_list if i]
    second_select_list = request.POST.getlist('second_select_list')
    second_list = [int(i) for i in second_select_list if i]
    mailgroup_select_list = request.POST.getlist('mailgroup_select_list')
    mailgroup_list = [int(i) for i in mailgroup_select_list if i]
    level_list = request.POST.getlist('level_list')
    errcode = 0
    msg = 'ok'
    try:
        gogroup_obj = asset_models.gogroup.objects.get(name=project_name)
    except asset_models.gogroup.DoesNotExist:
        errcode = 500
        msg = u'所选项目在数据库中不存在'
    else:
        try:
            project_obj = models.ProjectInfo.objects.get(group=gogroup_obj)
        except models.ProjectInfo.DoesNotExist:
            project_obj = models.ProjectInfo.objects.create(group=gogroup_obj)
            for owner in owner_list:
                project_obj.owner.add(owner)

            if first_list:
                for first in first_list:
                    project_obj.first_approver.add(first)

            if second_list:
                for second in second_list:
                    project_obj.second_approver.add(second)

            if mailgroup_list:
                for mailgroup in mailgroup_list:
                    project_obj.mail_group.add(mailgroup)

            for level_str in level_list:
                level = level_str.strip().split(',')
                start_of_week = level[0]
                end_of_week = level[1]
                start_time = level[2]
                end_time = level[3]
                approval_level = level[4]

                try:
                    approval_level_obj = models.ApprovalLevel.objects.get(name=approval_level)
                except models.ApprovalLevel.DoesNotExist:
                    errcode = 500
                    msg = u'所选审批级别不存在'
                    data = dict(code=errcode, msg=msg)
                    return HttpResponse(json.dumps(data), content_type='application/json')
                else:
                    models.TimeSlot.objects.get_or_create(project_info=project_obj,
                                                          start_of_week=start_of_week,
                                                          end_of_week=end_of_week, start_time=start_time,
                                                          end_time=end_time, approval_level=approval_level_obj)

        else:
            errcode = 500
            msg = u'此项目已经初始化'

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def PublishSheetList(request):
    publishsheets = models.PublishSheet.objects.all().order_by('publish_date', 'publish_time')

    tobe_approved_list = []
    approve_refused_list = []
    approve_passed_list = []
    for publish in publishsheets:
        publish_datetime_str = publish.publish_date + ' ' + publish.publish_time
        publish_datetime_format = time.strptime(publish_datetime_str, '%Y-%m-%d %H:%M')
        publish_datetime_int = time.mktime(publish_datetime_format)
        now_int = time.time()
        if publish_datetime_int < now_int and (publish.status == '1' or publish.status == '3'):
            publish.status = '5'
            publish.save()
        else:
            services_objs = publish.goservices.all().order_by('name')
            services_str = ', '.join(services_objs.values_list('name', flat=True))
            env = services_objs[0].get_env_display()
            gogroup = services_objs[0].group.name
            level = publish.approval_level.get_name_display()
            approve_level = publish.approval_level.name
            tmp_dict = utils.serialize_instance(publish)
            tmp_dict.update({'gogroup': gogroup, 'services_str': services_str, 'env': env, 'approve_level': approve_level, 'level': level})

            if publish.status == '1':
                tobe_approved_list.append(tmp_dict)
            elif publish.status == '2':
                approve_refused_list.append(tmp_dict)
            elif publish.status == '3':
                approve_passed_list.append(tmp_dict)
            else:
                pass

    errcode = 0
    msg = 'ok'
    data = dict(code=errcode, msg=msg, tobe_approved_list=tobe_approved_list, approve_refused_list=approve_refused_list, approve_passed_list=approve_passed_list)

    return render_to_response('publish/publish_sheets.html', data)


@login_required
def PublishSheetDoneList(request):
    publishsheets = models.PublishSheet.objects.all().order_by('publish_date', 'publish_time')

    done_list = []
    outtime_list = []
    for publish in publishsheets:
        services_objs = publish.goservices.all().order_by('name')
        services_str = ', '.join(services_objs.values_list('name', flat=True))
        env = services_objs[0].get_env_display()
        gogroup = services_objs[0].group.name
        level = publish.approval_level.get_name_display()
        approve_level = publish.approval_level.name
        tmp_dict = utils.serialize_instance(publish)
        tmp_dict.update({'gogroup': gogroup, 'services_str': services_str, 'env': env, 'approve_level': approve_level,
                         'level': level})

        if publish.status == '4':
            done_list.append(tmp_dict)
        elif publish.status == '5':
            outtime_list.append(tmp_dict)
        else:
            pass

    errcode = 0
    msg = 'ok'
    data = dict(code=errcode, msg=msg, done_list=done_list, outtime_list=outtime_list)

    return render_to_response('publish/publish_done.html', data)


@login_required
def createPublishSheet(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    project_name = request.POST['project_name']
    env_id = request.POST['env_id']
    tapd_url = request.POST['tapd_url']
    reboot_services_list = request.POST.getlist('reboot_services_list', [])
    sql = request.POST['sql']
    consul_key = request.POST['consul_key']
    publish_date = request.POST['publish_date']
    if '/' in publish_date:
        publish_date = '-'.join(publish_date.split('/'))

    publish_time = request.POST['publish_time']

    try:
        projectinfo_obj = models.ProjectInfo.objects.get(group__name=project_name)
    except models.ProjectInfo.DoesNotExist:
        errcode = 500
        msg = u'项目初始化信息不存在'
        data = dict(code=errcode, msg=msg)
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        goservices_objs = asset_models.goservices.objects.filter(env=env_id).filter(name__in=reboot_services_list)
        publishsheet_obj = models.PublishSheet()
        publishsheet_obj.creator = user
        publishsheet_obj.tapd_url = tapd_url
        publishsheet_obj.publish_date = publish_date
        publishsheet_obj.publish_time = publish_time
        publishsheet_obj.project_info = projectinfo_obj

        publish_week = datetime.strptime(publish_date, '%Y-%m-%d').isoweekday()

        timeslot_objs = models.TimeSlot.objects.filter(project_info=projectinfo_obj)
        slot = False
        if len(timeslot_objs) > 0:
            for time_obj in timeslot_objs:
                start_week_int = int(time_obj.start_of_week)
                end_week_int = int(time_obj.end_of_week)
                if start_week_int < publish_week < end_week_int:
                    publish_time_format = time.strptime(str(publish_date) + ' ' + str(publish_time), '%Y-%m-%d %H:%M')
                    start_time_format = time.strptime(str(publish_date) + ' ' + str(time_obj.start_time), '%Y-%m-%d %H:%M')
                    end_time_format = time.strptime(str(publish_date) + ' ' + str(time_obj.end_time), '%Y-%m-%d %H:%M')
                    publish_time_int = time.mktime(publish_time_format)
                    start_time_int = time.mktime(start_time_format)
                    end_time_int = time.mktime(end_time_format)
                    if start_time_int < publish_time_int < end_time_int:
                        publishsheet_obj.approval_level = time_obj.approval_level
                        slot = True
                        break
        if not slot:
            publishsheet_obj.approval_level = models.ApprovalLevel.objects.get(name='1')

        if sql:
            publishsheet_obj.sql = sql

        if consul_key:
            publishsheet_obj.consul_key = consul_key

        publishsheet_obj.save()

        for goservice in goservices_objs:
            publishsheet_obj.goservices.add(goservice)

        data = dict(code=errcode, msg=msg)
        return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def ApproveList(request):
    user = request.user
    publishsheets = models.PublishSheet.objects.all().order_by('publish_date', 'publish_time')

    tobe_approved_list = []
    approve_refused_list = []
    approve_passed_list = []
    for publish in publishsheets:
        services_objs = publish.goservices.all().order_by('name')
        services_str = ', '.join(services_objs.values_list('name', flat=True))
        env = services_objs[0].get_env_display()
        gogroup = services_objs[0].group.name
        approve_level = publish.approval_level.get_name_display()
        tmp_dict = utils.serialize_instance(publish)
        tmp_dict.update({'gogroup': gogroup, 'services_str': services_str, 'env': env, 'level': approve_level})

        if publish.status == '1':
            tobe_approved_list.append(tmp_dict)
        elif publish.status == '2':
            approve_refused_list.append(tmp_dict)
        else:
            approve_passed_list.append(tmp_dict)

    return render(request, 'publish/approve_list.html',
                  {'tobe_approved_list': tobe_approved_list, 'approve_refused_list': approve_refused_list, 'approve_passed_list': approve_passed_list})


@login_required
def ApproveInit(request):
    user = request.user
    sheet_id = request.GET['sheet_id']
    print sheet_id
    try:
        publishsheet = models.PublishSheet.objects.get(id=sheet_id)
    except models.PublishSheet.DoesNotExist:
        errcode = 500
        msg = u'发布单不存在'
        data = dict(code=errcode, msg=msg)
        return render_to_response('publish/publish_sheets.html', data)
    else:
        tmp_dict = utils.serialize_instance(publishsheet)
        errcode = 0
        msg = 'ok'
        data = dict(code=errcode, msg=msg, approve_sheet=tmp_dict)

        return render_to_response('publish/approve_sheet.html', data)
