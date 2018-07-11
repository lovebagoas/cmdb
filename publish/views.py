# coding:utf8
import json

from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from publish import models
from asset import models as asset_models


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
    print project_tuple
    return render(request, 'publish/gogroup_init.html',
                  {'gogroup_objs': gogroup_objs, 'mailgroup_objs': mailgroup_objs, 'user_objs': user_objs, 'project_tuple': project_tuple})


@login_required
def createProject(request):
    project_id = int(request.POST['project_id'])
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
        gogroup_obj = asset_models.gogroup.objects.get(id=project_id)
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
