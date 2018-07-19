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

    project_list = []
    projectinfo_objs = models.ProjectInfo.objects.all().order_by('group__name')
    for projectinfo in projectinfo_objs:
        tmp_dict = {
            'project_id': projectinfo.id,
            'project_name': projectinfo.group.name,
            'owner_list': [owner.username for owner in projectinfo.owner.all()],
            'mailgroup_list': [owner.email for owner in projectinfo.mail_group.all()],
            'first_list': [owner.username for owner in projectinfo.first_approver.all()],
            'second_list': [owner.username for owner in projectinfo.second_approver.all()],
        }
        project_list.append(tmp_dict)

    return render(request, 'publish/gogroup_init.html',
                  {'gogroup_objs': gogroup_objs, 'mailgroup_objs': mailgroup_objs, 'user_objs': user_objs,
                   'project_list': project_list})


@login_required
def createProject(request):
    user = request.user
    project_select_list = request.POST.getlist('project_select_list')
    project_id_list = [int(project_id) for project_id in project_select_list]
    owner_select_list = request.POST.getlist('owner_select_list')
    owner_list = [int(i) for i in owner_select_list]
    first_select_list = request.POST.getlist('first_select_list')
    first_list = [int(i) for i in first_select_list if i]
    second_select_list = request.POST.getlist('second_select_list')
    second_list = [int(i) for i in second_select_list if i]
    mailgroup_select_list = request.POST.getlist('mailgroup_select_list')
    mailgroup_list = [int(i) for i in mailgroup_select_list if i]

    errcode = 0
    msg = 'ok'

    gogroup_objs = asset_models.gogroup.objects.filter(id__in=project_id_list)
    if len(gogroup_objs) == 0:
        errcode = 500
        msg = u'所选项目不存在'
        data = dict(code=errcode, msg=msg)
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        for gogroup_obj in gogroup_objs:
            print gogroup_obj
            try:
                project_obj = models.ProjectInfo.objects.get(group=gogroup_obj)
            except models.ProjectInfo.DoesNotExist:
                project_obj = models.ProjectInfo.objects.create(group=gogroup_obj, creator=user)
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

            else:
                print 'already exist'
                errcode = 500
                msg = project_obj.group.name + u'项目初始化信息已存在'
                data = dict(code=errcode, msg=msg)
                return HttpResponse(json.dumps(data), content_type='application/json')

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def projectDelete(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    projectinfo_id = int(request.POST['projectinfo_id'])

    try:
        project_obj = models.ProjectInfo.objects.get(id=projectinfo_id)
    except models.ProjectInfo.DoesNotExist:
        errcode = 500
        msg = u'所选项目初始化信息不存在'
    else:
        try:
            project_obj.creator
        except:
            project_obj.creator = None
            project_obj.save()

        if user == project_obj.creator:
            project_obj.delete()
        else:
            owner_list = project_obj.owner.all()
            if user in owner_list:
                project_obj.delete()
            else:
                errcode = 500
                msg = u'你不是此项目的负责人，不能删除'

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def LevelList(request):
    project_objs = models.ProjectInfo.objects.all().order_by('group__name')

    timeslot_objs = models.TimeSlotLevel.objects.filter().order_by('-is_global', 'approval_level__name', 'start_of_week', 'end_of_week', 'start_time', 'end_time')
    level_list = []
    for timeslot in timeslot_objs:
        project_list = timeslot.project_timeslotlevel.all().order_by('group__name')
        if project_list:
            level_list.append({'timeslot': timeslot, 'project_list': project_list})

    return render(request, 'publish/level_list.html', {'level_list': level_list, 'project_objs': project_objs})


@login_required
def LevelDetail(request):
    errcode = 0
    msg = 'ok'
    content = {}

    timeslot_id = int(request.GET['timeslot_id'])

    try:
        timeslot_obj = models.TimeSlotLevel.objects.get(id=timeslot_id)
    except models.TimeSlotLevel.DoesNotExist:
        errcode = 500
        msg = u'所选等级不存在'
    else:
        content['level_type'] = timeslot_obj.get_is_global_display()
        content['creator'] = timeslot_obj.creator.username
        content['time'] = timeslot_obj.get_start_of_week_display() + ' ~ ' + timeslot_obj.get_end_of_week_display() + ' ' + timeslot_obj.start_time + ' ~ ' + timeslot_obj.end_time
        content['approval_level'] = timeslot_obj.approval_level.get_name_display()
        approval_level = timeslot_obj.approval_level.name
        content['project_list'] = []
        project_objs = timeslot_obj.project_timeslotlevel.all().order_by('group__name')
        for projectinfo in project_objs:
            if approval_level == '1':
                first_list = []
                second_list = []
            elif approval_level == '2':
                first_list = [owner.username for owner in projectinfo.first_approver.all()]
                second_list = []
            else:
                first_list = [owner.username for owner in projectinfo.first_approver.all()]
                second_list = [owner.username for owner in projectinfo.second_approver.all()]
            tmp_dict = {
                'project_name': projectinfo.group.name,
                'owner_list': [owner.username for owner in projectinfo.owner.all()],
                'mailgroup_list': [owner.email for owner in projectinfo.mail_group.all()],
                'first_list': first_list,
                'second_list': second_list,
            }
            content['project_list'].append(tmp_dict)

    print 'content : '
    print content
    data = dict(code=errcode, msg=msg, content=content)
    return render_to_response('publish/level_detail_modal.html', data)


@login_required
def LevelCreate(request):
    errcode = 0
    msg = 'ok'
    user = request.user

    radio = request.POST['radio']
    level_list = request.POST.getlist('level_list')
    project_select_list = request.POST.getlist('project_select_list')
    project_id_list = [int(project_id) for project_id in project_select_list]
    project_objs = models.ProjectInfo.objects.filter(id__in=project_id_list)

    if len(project_objs) == 0:
        errcode = 500
        msg = u'所选项目初始化信息不存在'
        data = dict(code=errcode, msg=msg)
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        for project_obj in project_objs:
            if radio == '1':
                print 'radio 1'
                old_time_objs = project_obj.timeslot_level.all()
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
                        time_obj = models.TimeSlotLevel.objects.get_or_create(start_of_week=start_of_week,
                                                                              end_of_week=end_of_week,
                                                                              start_time=start_time,
                                                                              end_time=end_time,
                                                                              approval_level=approval_level_obj,
                                                                              creator=user)
                        print time_obj
                        if time_obj not in old_time_objs:
                            project_obj.timeslot_level.add(time_obj[0])
            else:
                print 'radio 2'
                old_time_objs = project_obj.timeslot_level.all()
                print 'old_time_objs : ', old_time_objs
                level_id_list = [int(level_id) for level_id in level_list]
                time_objs = models.TimeSlotLevel.objects.filter(id__in=level_id_list)
                for time_obj in time_objs:
                    print 'time_obj : ', time_obj
                    if time_obj not in old_time_objs:
                        print 'add'
                        project_obj.timeslot_level.add(time_obj)

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def LevelDelete(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    timeslot_id = int(request.POST['timeslot_id'])
    print 'timeslot_id : ', timeslot_id

    try:
        timeslot_obj = models.TimeSlotLevel.objects.get(id=timeslot_id)
    except models.TimeSlotLevel.DoesNotExist:
        errcode = 500
        msg = u'所选项目审批级别不存在'
    else:
        if timeslot_obj.creator:
            if timeslot_obj.creator == user:
                timeslot_obj.delete()
            else:
                errcode = 500
                msg = u'你不是创建人，不能删除'
        else:
            timeslot_obj.delete()

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def templateList(request):
    timeslot_objs = models.TimeSlotLevel.objects.filter(is_global='2').order_by('approval_level__name', 'start_of_week', 'end_of_week', 'start_time', 'end_time')
    return render(request, 'publish/template_list.html', {'timeslot_objs': timeslot_objs})


@login_required
def templateCheckboxList(request):
    timeslot_objs = models.TimeSlotLevel.objects.filter(is_global='2').order_by('approval_level__name', 'start_of_week', 'end_of_week', 'start_time', 'end_time')
    return render(request, 'publish/template_checbox.html', {'timeslot_objs': timeslot_objs})


@login_required
def templateCreate(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    weekday_start = request.POST['weekday_start']
    weekday_end = request.POST['weekday_end']
    time_start = request.POST['time_start']
    time_end = request.POST['time_end']
    level = request.POST['level']

    try:
        level_obj = models.ApprovalLevel.objects.get(name=level)
    except models.ApprovalLevel.DoesNotExist:
        errcode = 500
        msg = u'所选等级不存在'
    else:
        try:
            models.TimeSlotLevel.objects.get(start_of_week=weekday_start, end_of_week=weekday_end,
                                             start_time=time_start, end_time=time_end, approval_level=level_obj, is_global='2')
        except models.TimeSlotLevel.DoesNotExist:
            models.TimeSlotLevel.objects.create(start_of_week=weekday_start, end_of_week=weekday_end,
                                                start_time=time_start, end_time=time_end, approval_level=level_obj, is_global='2',
                                                creator=user)
        else:
            errcode = 500
            msg = u'相同【时间段<--->级别】已存在'

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


def templateDelete(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    timeslot_id = int(request.POST['timeslot_id'])

    try:
        timeslot_obj = models.TimeSlotLevel.objects.get(id=timeslot_id)
    except models.TimeSlotLevel.DoesNotExist:
        errcode = 500
        msg = u'所选【时间段<--->级别】不存在'
    else:
        if timeslot_obj.creator:
            if timeslot_obj.creator == user:
                timeslot_obj.delete()
            else:
                errcode = 500
                msg = u'你不是创建人，不能删除'
        else:
            timeslot_obj.delete()

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
        if publish_datetime_int < now_int and publish.status == '1':
            # 超时未审批
            publish.status = '6'
            publish.save()
        elif publish_datetime_int < now_int and publish.status == '3':
            # 超时未发布
            publish.status = '5'
            publish.save()
        else:
            services_objs = publish.goservices.all().order_by('name')
            services_str = ', '.join(services_objs.values_list('name', flat=True))
            env = services_objs[0].get_env_display()
            gogroup_obj = services_objs[0].group
            level = publish.approval_level.get_name_display()
            approve_level = publish.approval_level.name

            if approve_level == '1':
                first_str = ''
                second_str = ''
            elif approve_level == '2':
                first_list = [owner.username for owner in publish.first_approver.all()]
                first_str = ', '.join(first_list)
                second_str = ''
            else:
                first_list = [owner.username for owner in publish.first_approver.all()]
                first_str = ', '.join(first_list)
                second_list = [owner.username for owner in publish.second_approver.all()]
                second_str = ', '.join(second_list)

            tmp_dict = utils.serialize_instance(publish)
            if len(publish.sql) > 40:
                tmp_dict['sql'] = utils.cut_str(publish.sql, 40)
            if len(publish.consul_key) > 40:
                tmp_dict['consul_key'] = utils.cut_str(publish.consul_key, 40)
            tmp_dict.update({'id': publish.id, 'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env,
                             'approve_level': approve_level, 'level': level, 'first_str': first_str, 'second_str': second_str, 'creator': publish.creator.username})

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
    data = dict(code=errcode, msg=msg, tobe_approved_list=tobe_approved_list, approve_refused_list=approve_refused_list,
                approve_passed_list=approve_passed_list)

    return render_to_response('publish/publish_sheets.html', data)


@login_required
def PublishSheetDoneList(request):
    publishsheets = models.PublishSheet.objects.all().order_by('publish_date', 'publish_time')

    done_list = []
    outtime_notpublish_list = []
    outtime_notapprove_list = []
    for publish in publishsheets:
        services_objs = publish.goservices.all().order_by('name')
        services_str = ', '.join(services_objs.values_list('name', flat=True))
        env = services_objs[0].get_env_display()
        gogroup_obj = services_objs[0].group
        level = publish.approval_level.get_name_display()
        approve_level = publish.approval_level.name

        if approve_level == '1':
            first_str = ''
            second_str = ''
        elif approve_level == '2':
            first_list = [owner.username for owner in publish.first_approver.all()]
            first_str = ', '.join(first_list)
            second_str = ''
        else:
            first_list = [owner.username for owner in publish.first_approver.all()]
            first_str = ', '.join(first_list)
            second_list = [owner.username for owner in publish.second_approver.all()]
            second_str = ', '.join(second_list)

        tmp_dict = utils.serialize_instance(publish)
        if len(publish.sql) > 40:
            tmp_dict['sql'] = utils.cut_str(publish.sql, 40)
        if len(publish.consul_key) > 40:
            tmp_dict['consul_key'] = utils.cut_str(publish.consul_key, 40)
        tmp_dict.update({'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env, 'approve_level': approve_level,
                         'level': level, 'first_str': first_str, 'second_str': second_str, 'creator': publish.creator.username})

        if publish.status == '4':
            done_list.append(tmp_dict)
        elif publish.status == '5':
            outtime_notpublish_list.append(tmp_dict)
        elif publish.status == '6':
            outtime_notapprove_list.append(tmp_dict)
        else:
            pass

    errcode = 0
    msg = 'ok'
    data = dict(code=errcode, msg=msg, done_list=done_list, outtime_notpublish_list=outtime_notpublish_list,
                outtime_notapprove_list=outtime_notapprove_list)

    return render_to_response('publish/publish_done.html', data)


@login_required
def PublishSheetRefuseReason(request):
    errcode = 0
    msg = 'ok'
    content = {}

    sheet_id = int(request.GET['sheet_id'])

    try:
        sheet_obj = models.PublishSheet.objects.get(id=sheet_id)
    except models.PublishSheet.DoesNotExist:
        errcode = 500
        msg = u'所选发布单不存在'
    else:
        try:
            sheet_history_obj = models.PublishApprovalHistory.objects.get(publish_sheet=sheet_obj, approve_status=2)
        except models.PublishApprovalHistory.DoesNotExist:
            errcode = 500
            msg = u'所选发布单审批记录不存在'
        else:
            content['approve_count'] = sheet_history_obj.approve_count
            if sheet_obj.approval_level.name == '2':
                # 一级审批, 被拒绝
                content['first_approver'] = sheet_history_obj.first_approver.username
                content['first_approve_time'] = sheet_history_obj.first_approve_time
                content['refuse_reason'] = sheet_history_obj.refuse_reason
            else:
                # 二级审批
                if sheet_history_obj.approve_count == '1':
                    # 一级审批被拒绝
                    content['first_approver'] = sheet_history_obj.first_approver.username
                    content['first_approve_time'] = sheet_history_obj.first_approve_time
                    content['refuse_reason'] = sheet_history_obj.refuse_reason
                else:
                    # 二级审批被拒绝
                    content['first_approver'] = sheet_history_obj.second_approver.username
                    content['first_approve_time'] = sheet_history_obj.first_approve_time
                    content['second_approver'] = sheet_history_obj.second_approver.username
                    content['second_approve_time'] = sheet_history_obj.second_approve_time
                    content['refuse_reason'] = sheet_history_obj.refuse_reason

    data = dict(code=errcode, msg=msg, content=content)
    return render_to_response('publish/publish_sheet_refusereason.html', data)


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
        gogroup_obj = asset_models.gogroup.objects.get(name=project_name)
    except asset_models.gogroup.DoesNotExist:
        errcode = 500
        msg = u'go项目不存在'
        data = dict(code=errcode, msg=msg)
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        try:
            projectinfo_obj = models.ProjectInfo.objects.get(group=gogroup_obj)
        except models.ProjectInfo.DoesNotExist:
            print 'no project info of this gogroup'
            projectinfo_obj = None

        publishsheet_obj = models.PublishSheet()
        publishsheet_obj.creator = user
        publishsheet_obj.tapd_url = tapd_url
        publishsheet_obj.publish_date = publish_date
        publishsheet_obj.publish_time = publish_time
        publishsheet_obj.sql = sql
        publishsheet_obj.consul_key = consul_key
        publishsheet_obj.status = '1'

        slot = False  # 是否有级别定义
        publish_week = datetime.strptime(publish_date, '%Y-%m-%d').isoweekday()

        # 查看节假日时间段，二级审批
        festival_objs = models.Festival.objects.all()
        if len(festival_objs) > 0:
            for festival_obj in festival_objs:
                publish_time_format = time.strptime(str(publish_date) + ' ' + str(publish_time), '%Y-%m-%d %H:%M')
                publish_time_int = time.mktime(publish_time_format)
                start_time_format = time.strptime(festival_obj.start_day.strftime("%Y-%m-%d %H:%M"), '%Y-%m-%d %H:%M')
                start_time_int = time.mktime(start_time_format)
                if festival_obj.end_day:
                    end_time_format = time.strptime(festival_obj.end_day.strftime("%Y-%m-%d %H:%M"), '%Y-%m-%d %H:%M')
                    end_time_int = time.mktime(end_time_format)
                else:
                    end_time_int = start_time_int + 86400

                if start_time_int <= publish_time_int <= end_time_int:
                    publishsheet_obj.approval_level = models.ApprovalLevel.objects.get(name='3')
                    print 'festival done'
                    slot = True
                    break

        # 查看通用模板时间段
        template_objs = models.TimeSlotLevel.objects.filter(is_global='2')
        if len(template_objs) > 0:
            for template_obj in template_objs:
                start_week_int = int(template_obj.start_of_week)
                end_week_int = int(template_obj.end_of_week)
                print 'template  start_week_int : ', start_week_int
                print 'template  end_week_int : ', end_week_int
                print 'template  publish_week : ', publish_week
                if start_week_int <= publish_week <= end_week_int:
                    publish_time_format = time.strptime(str(publish_date) + ' ' + str(publish_time), '%Y-%m-%d %H:%M')
                    start_time_format = time.strptime(str(publish_date) + ' ' + str(template_obj.start_time),
                                                      '%Y-%m-%d %H:%M')
                    end_time_format = time.strptime(str(publish_date) + ' ' + str(template_obj.end_time), '%Y-%m-%d %H:%M')
                    publish_time_int = time.mktime(publish_time_format)
                    start_time_int = time.mktime(start_time_format)
                    end_time_int = time.mktime(end_time_format)
                    if start_time_int == end_time_int:
                        end_time_int = end_time_int + 86400
                    if start_time_int <= publish_time_int <= end_time_int:
                        publishsheet_obj.approval_level = template_obj.approval_level
                        print 'template done'
                        slot = True
                        break

        if not slot:
            # 查看自定义模板时间段
            if projectinfo_obj:
                custom_objs = projectinfo_obj.timeslot_level.all()
                if len(custom_objs) > 0:
                    for custom_obj in custom_objs:
                        start_week_int = int(custom_obj.start_of_week)
                        end_week_int = int(custom_obj.end_of_week)
                        if start_week_int <= publish_week <= end_week_int:
                            publish_time_format = time.strptime(str(publish_date) + ' ' + str(publish_time),
                                                                '%Y-%m-%d %H:%M')
                            start_time_format = time.strptime(str(publish_date) + ' ' + str(custom_obj.start_time),
                                                              '%Y-%m-%d %H:%M')
                            end_time_format = time.strptime(str(publish_date) + ' ' + str(custom_obj.end_time),
                                                            '%Y-%m-%d %H:%M')
                            publish_time_int = time.mktime(publish_time_format)
                            start_time_int = time.mktime(start_time_format)
                            end_time_int = time.mktime(end_time_format)
                            if start_time_int <= publish_time_int <= end_time_int:
                                publishsheet_obj.approval_level = custom_obj.approval_level
                                print 'custom done'
                                slot = True
                                break

        if not slot:
            print 'no need done'
            publishsheet_obj.approval_level = models.ApprovalLevel.objects.get(name='1')

        publishsheet_obj.save()

        if projectinfo_obj:
            # 添加审批人
            publishsheet_obj.first_approver = projectinfo_obj.first_approver.all()
            publishsheet_obj.second_approver = projectinfo_obj.second_approver.all()

        goservices_objs = asset_models.goservices.objects.filter(env=env_id).filter(name__in=reboot_services_list, group=gogroup_obj)
        for goservice in goservices_objs:
            publishsheet_obj.goservices.add(goservice)

        data = dict(code=errcode, msg=msg)
        return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def PublishSheetDelete(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    sheet_id = int(request.POST['sheet_id'])

    try:
        publish_obj = models.PublishSheet.objects.get(id=sheet_id)
    except models.PublishSheet.DoesNotExist:
        errcode = 500
        msg = u'所选发布单不存在'
    else:
        if publish_obj.creator:
            if publish_obj.creator == user:
                publish_obj.delete()
            else:
                errcode = 500
                msg = u'你不是创建人，不能删除'
        else:
            print 'no creator'
            publish_obj.delete()

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
        publish_datetime_str = publish.publish_date + ' ' + publish.publish_time
        publish_datetime_format = time.strptime(publish_datetime_str, '%Y-%m-%d %H:%M')
        publish_datetime_int = time.mktime(publish_datetime_format)
        now_int = time.time()
        if publish_datetime_int < now_int and publish.status == '1':
            # 超时未审批
            publish.status = '6'
            publish.save()
        else:
            services_objs = publish.goservices.all().order_by('name')
            services_str = ', '.join(services_objs.values_list('name', flat=True))
            env = services_objs[0].get_env_display()
            gogroup_obj = services_objs[0].group
            level = publish.approval_level.get_name_display()
            approve_level = publish.approval_level.name

            if approve_level == '1':
                first_str = ''
                second_str = ''
                first_list = []
                second_list = []
            elif approve_level == '2':
                first_list = [owner.username for owner in publish.first_approver.all()]
                second_list = []
                first_str = ', '.join(first_list)
                second_str = ''
            else:
                first_list = [owner.username for owner in publish.first_approver.all()]
                first_str = ', '.join(first_list)
                second_list = [owner.username for owner in publish.second_approver.all()]
                second_str = ', '.join(second_list)

            tmp_dict = utils.serialize_instance(publish)
            if len(publish.sql) > 40:
                tmp_dict['sql'] = utils.cut_str(publish.sql, 40)
            if len(publish.consul_key) > 40:
                tmp_dict['consul_key'] = utils.cut_str(publish.consul_key, 40)

            if user.username in first_list:
                tmp_dict.update({'id': publish.id, 'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env,
                         'approve_level': approve_level, 'level': level, 'first_str': first_str, 'second_str': second_str, 'creator': publish.creator.username, 'can_approve': True})
                if publish.status == '1':
                    tobe_approved_list.append(tmp_dict)
                elif publish.status == '2':
                    approve_refused_list.append(tmp_dict)
                else:
                    approve_passed_list.append(tmp_dict)
            elif user.username in second_list:
                tmp_dict.update(
                    {'id': publish.id, 'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env,
                     'approve_level': approve_level, 'level': level, 'first_str': first_str, 'second_str': second_str,
                     'creator': publish.creator.username, 'can_approve': False})
                if publish.status == '1':
                    tobe_approved_list.append(tmp_dict)
                elif publish.status == '2':
                    approve_refused_list.append(tmp_dict)
                else:
                    approve_passed_list.append(tmp_dict)
            print 'tmp_dict : '
            print tmp_dict

    return render(request, 'publish/approve_list.html',
                  {'tobe_approved_list': tobe_approved_list, 'approve_refused_list': approve_refused_list,
                   'approve_passed_list': approve_passed_list})


@login_required
def ApproveInit(request):
    user = request.user
    sheet_id = request.GET['sheet_id']
    errcode = 0
    msg = 'ok'
    try:
        publishsheet = models.PublishSheet.objects.get(id=sheet_id)
    except models.PublishSheet.DoesNotExist:
        errcode = 500
        msg = u'发布单不存在'
        data = dict(code=errcode, msg=msg)
        return render_to_response('publish/publish_sheets.html', data)
    else:
        try:
            publish_history = models.PublishApprovalHistory.objects.get(publish_sheet=publishsheet)
        except models.PublishApprovalHistory.DoesNotExist:
            # 从未审批过
            tmp_dict = utils.serialize_instance(publishsheet)
            service_objs = publishsheet.goservices.all()
            gogroup = service_objs[0].group
            tmp_dict.update({
                'group_name': gogroup.name,
                'services': ', '.join(service_objs.values_list('name', flat=True)),
                'env': service_objs[0].get_env_display()
            })
        else:
            # 被第一审批通过
            first_approver = publish_history.first_approver
            first_approve_time = publish_history.first_approve_time
            # first_notices = publish_history.first_notices
            approve_status = publish_history.approve_status

            tmp_dict = utils.serialize_instance(publishsheet)
            service_objs = publishsheet.goservices.all()
            gogroup = service_objs[0].group
            tmp_dict.update({
                'group_name': gogroup.name,
                'services': ', '.join(service_objs.values_list('name', flat=True)),
                'env': service_objs[0].get_env_display(),
                'first_approver': first_approver,
                'first_approve_time': first_approve_time,
                # 'first_notices': first_notices,
                'approve_status': approve_status
            })

        data = dict(code=errcode, msg=msg, approve_sheet=tmp_dict)
        return render_to_response('publish/approve_sheet.html', data)


@login_required
def ApproveJudge(request):
    user = request.user
    publish_id = int(request.POST['publish_id'])
    approve = request.POST['approve']
    text = request.POST['text']
    errcode = 0
    msg = 'ok'
    try:
        publishsheet = models.PublishSheet.objects.get(id=publish_id)
    except models.PublishSheet.DoesNotExist:
        errcode = 500
        msg = u'发布单不存在'
        data = dict(code=errcode, msg=msg)
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        try:
            publish_history = models.PublishApprovalHistory.objects.get(publish_sheet=publishsheet)
        except models.PublishApprovalHistory.DoesNotExist:
            # 从未审批过
            publish_history = models.PublishApprovalHistory()
            publish_history.publish_sheet = publishsheet
            publish_history.approve_count = '1'
            publish_history.approve_status = approve
            publish_history.first_approver = user
            publish_history.first_approve_time = datetime.now()
            if approve == '1':
                # publish_history.first_notices = text
                publishsheet.status = '3'
                publishsheet.save()
            else:
                publish_history.refuse_reason = text
                publishsheet.status = '2'
                publishsheet.save()
            publish_history.save()
        else:
            # 被第一审批通过
            publish_history.approve_count = '2'
            publish_history.approve_status = approve
            publish_history.second_approver = user
            publish_history.second_approve_time = datetime.now()
            if approve == '1':
                # publish_history.first_notices = text
                publishsheet.status = '3'
                publishsheet.save()
            else:
                publish_history.refuse_reason = text
                publishsheet.status = '2'
                publishsheet.save()
            publish_history.save()

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')