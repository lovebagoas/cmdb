# coding:utf8
import json
from datetime import datetime
import time

from django.shortcuts import render, HttpResponse, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from publish import models
from publish import utils
from asset import models as asset_models
from asset import utils as asset_utils


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
            'creator': projectinfo.creator.username,
        }
        project_list.append(tmp_dict)

    return render(request, 'publish/gogroup_init.html',
                  {'gogroup_objs': gogroup_objs, 'mailgroup_objs': mailgroup_objs, 'user_objs': user_objs,
                   'project_list': project_list})


@login_required
def createProject(request):
    user = request.user
    ip = request.META['REMOTE_ADDR']
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

                asset_utils.logs(user.username, ip, 'create project info', 'success')

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
    ip = request.META['REMOTE_ADDR']
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
            asset_utils.logs(user.username, ip, 'delete project info', 'success')
        else:
            owner_list = project_obj.owner.all()
            if user in owner_list:
                asset_utils.logs(user.username, ip, 'delete project info', 'success')
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
            level_list.append({'timeslot': timeslot, 'project_list': project_list, 'creator': timeslot.creator.username})

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

    data = dict(code=errcode, msg=msg, content=content)
    return render_to_response('publish/level_detail_modal.html', data)


@login_required
def LevelCreate(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    ip = request.META['REMOTE_ADDR']

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
            first_approver_objs = project_obj.first_approver.all()
            second_approver_objs = project_obj.second_approver.all()
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

                    if approval_level == '2' and not first_approver_objs:
                        errcode = 500
                        msg = u'项目 {0} 无一级审批人'.format(project_obj.group.name)
                        data = dict(code=errcode, msg=msg)
                        asset_utils.logs(user.username, ip, 'create project--approval level, no first approver', 'failed')
                        return HttpResponse(json.dumps(data), content_type='application/json')
                    if approval_level == '3' and not second_approver_objs:
                        errcode = 500
                        msg = u'项目 {0} 无二级审批人'.format(project_obj.group.name)
                        data = dict(code=errcode, msg=msg)
                        asset_utils.logs(user.username, ip, 'create project--approval level, no second approver',
                                         'failed')
                        return HttpResponse(json.dumps(data), content_type='application/json')

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
                            asset_utils.logs(user.username, ip, 'create project--approval level',
                                             'success')
            else:
                print 'radio 2'
                old_time_objs = project_obj.timeslot_level.all()
                print 'LevelCreate--old_time_objs : ', old_time_objs
                timeslot_id_list = [int(level_id) for level_id in level_list]
                time_objs = models.TimeSlotLevel.objects.filter(id__in=timeslot_id_list)
                for time_obj in time_objs:
                    if time_obj.approval_level.name == '2' and not first_approver_objs:
                        errcode = 500
                        msg = u'项目 {0} 无一级审批人'.format(project_obj.group.name)
                        data = dict(code=errcode, msg=msg)
                        asset_utils.logs(user.username, ip, 'create project--approval level, no first approver',
                                         'failed')
                        return HttpResponse(json.dumps(data), content_type='application/json')
                    if time_obj.approval_level.name == '3' and not second_approver_objs:
                        errcode = 500
                        msg = u'项目 {0} 无二级审批人'.format(project_obj.group.name)
                        data = dict(code=errcode, msg=msg)
                        asset_utils.logs(user.username, ip, 'create project--approval level, no second approver',
                                         'failed')
                        return HttpResponse(json.dumps(data), content_type='application/json')

                    print 'LevelCreate--time_obj : ', time_obj
                    if time_obj not in old_time_objs:
                        print 'LevelCreate--add'
                        asset_utils.logs(user.username, ip, 'create project--approval level',
                                         'success')
                        project_obj.timeslot_level.add(time_obj)

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def LevelDelete(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    ip = request.META['REMOTE_ADDR']
    timeslot_id = int(request.POST['timeslot_id'])
    print 'timeslot_id : ', timeslot_id

    try:
        timeslot_obj = models.TimeSlotLevel.objects.get(id=timeslot_id)
    except models.TimeSlotLevel.DoesNotExist:
        errcode = 500
        msg = u'所选项目审批级别不存在'
    else:
        projectinfo_objs = timeslot_obj.project_timeslotlevel.all()
        for projectinfo in projectinfo_objs:
            projectinfo.timeslot_level.remove(timeslot_obj)
        asset_utils.logs(user.username, ip, 'delete project--approval level', 'success')

        if timeslot_obj.creator:
            if timeslot_obj.creator == user:
                asset_utils.logs(user.username, ip, 'delete project--approval level', 'success')
                timeslot_obj.delete()
            else:
                errcode = 500
                msg = u'你不是此审批级别创建人，不能删除'
        else:
            asset_utils.logs(user.username, ip, 'delete project--approval level', 'success')
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
    ip = request.META['REMOTE_ADDR']
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
            asset_utils.logs(user.username, ip, 'create approval level template', 'success')
        else:
            errcode = 500
            msg = u'相同【时间段<--->级别】已存在'

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


def templateDelete(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    ip = request.META['REMOTE_ADDR']
    timeslot_id = int(request.POST['timeslot_id'])

    try:
        timeslot_obj = models.TimeSlotLevel.objects.get(id=timeslot_id)
    except models.TimeSlotLevel.DoesNotExist:
        errcode = 500
        msg = u'所选【时间段<--->级别】不存在'
    else:
        if timeslot_obj.creator:
            if timeslot_obj.creator == user:
                asset_utils.logs(user.username, ip, 'delete approval level template', 'success')
                timeslot_obj.delete()
            else:
                errcode = 500
                msg = u'你不是创建人，不能删除'
        else:
            asset_utils.logs(user.username, ip, 'delete approval level template', 'success')
            timeslot_obj.delete()

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def PublishSheetList(request):
    page1 = request.GET.get('page1', 1)
    page2 = request.GET.get('page2', 1)
    page3 = request.GET.get('page3', 1)
    errcode = 0
    msg = 'ok'
    user = request.user
    publishsheets = models.PublishSheet.objects.all().order_by('publish_date', 'publish_time')

    tobe_approved_list = []
    approve_refused_list = []
    approve_passed_list = []
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

        tmp_dict.update({'id': publish.id, 'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env,
                             'approve_level': approve_level, 'level': level, 'first_str': first_str, 'second_str': second_str, 'creator': publish.creator.username})

        if user == publish.creator:
            tmp_dict['can_publish'] = True
        else:
            tmp_dict['can_publish'] = False

        # 判断是否超时
        publish_datetime_str = publish.publish_date + ' ' + publish.publish_time
        publish_datetime_format = time.strptime(publish_datetime_str, '%Y-%m-%d %H:%M')
        publish_datetime_int = time.mktime(publish_datetime_format)
        now_int = time.time()
        if publish_datetime_int <= now_int:
            if publish.status == '2' or publish.status == '4' or publish.status == '5' or publish.status == '6':
                pass
            else:
                # 超时
                if publish.status == '1':
                    # 状态为审批中
                    print 'publish.id : ', publish.id
                    if publish.approval_level.name == '1':
                        # 无需审批的单子
                        if publish_datetime_int + 900 < now_int:
                            # 超时15分钟未发布
                            publish.status = '5'
                            publish.save()
                        else:
                            print 'here----can_publish'
                            # 超时15分钟之内，可以发布
                            tmp_dict['can_publish'] = True
                            approve_passed_list.append(tmp_dict)
                    else:
                        # 一级审批和二级审批的单子，超时未审批
                        publish.status = '6'
                        publish.save()
                else:
                    # 状态为审批通过
                    if publish.approval_level.name == '2':
                        # 一级审批
                        if publish_datetime_int + 900 < now_int:
                            # 超时15分钟未发布
                            publish.status = '5'
                            publish.save()
                        else:
                            # 超时15分钟之内，可以发布
                            tmp_dict['can_publish'] = True
                            approve_passed_list.append(tmp_dict)
                    else:
                        # 二级审批
                        try:
                            history_obj = models.PublishApprovalHistory.objects.get(publish_sheet=publish)
                        except models.PublishApprovalHistory.DoesNotExist:
                            errcode = 500
                            msg = u'审批历史不存在'
                        else:
                            if history_obj.approve_count == '1':
                                # 第二级审批人，超时未审批
                                publish.status = '6'
                                publish.save()
                            else:
                                if publish_datetime_int + 900 < now_int:
                                    # 超时15分钟未发布
                                    publish.status = '5'
                                    publish.save()
                                else:
                                    # 超时15分钟之内，可以发布
                                    tmp_dict['can_publish'] = True
                                    approve_passed_list.append(tmp_dict)
        else:
            tmp_dict['can_publish'] = False
            if publish.approval_level.name == '1':
                # 无需审批
                approve_passed_list.append(tmp_dict)
            elif publish.approval_level.name == '2':
                # 一级审批
                if publish.status == '1':
                    tobe_approved_list.append(tmp_dict)
                elif publish.status == '2':
                    approve_refused_list.append(tmp_dict)
                elif publish.status == '3':
                    approve_passed_list.append(tmp_dict)
            else:
                # 二级审批
                if publish.status == '1':
                    tobe_approved_list.append(tmp_dict)
                elif publish.status == '2':
                    approve_refused_list.append(tmp_dict)
                elif publish.status == '3':
                    # 判断一级审批完成还是二级审批完成
                    try:
                        history_obj = models.PublishApprovalHistory.objects.get(publish_sheet=publish)
                    except models.PublishApprovalHistory.DoesNotExist:
                        errcode = 500
                        msg = u'审批历史不存在'
                    else:
                        if history_obj.approve_count == '1':
                            tobe_approved_list.append(tmp_dict)
                        else:
                            approve_passed_list.append(tmp_dict)

    # # 分页
    # paginator = Paginator(tobe_approved_list, 2)
    # try:
    #     tobe_approved_list = paginator.page(page1)
    # except PageNotAnInteger:
    #     tobe_approved_list = paginator.page(1)
    # except EmptyPage:
    #     tobe_approved_list = paginator.page(paginator.num_pages)
    #
    # paginator = Paginator(approve_refused_list, 2)
    # try:
    #     approve_refused_list = paginator.page(page2)
    # except PageNotAnInteger:
    #     approve_refused_list = paginator.page(1)
    # except EmptyPage:
    #     approve_refused_list = paginator.page(paginator.num_pages)
    #
    # paginator = Paginator(approve_passed_list, 2)
    # try:
    #     approve_passed_list = paginator.page(page3)
    # except PageNotAnInteger:
    #     approve_passed_list = paginator.page(1)
    # except EmptyPage:
    #     approve_passed_list = paginator.page(paginator.num_pages)

    data = dict(code=errcode, msg=msg, tobe_approved_list=tobe_approved_list, approve_refused_list=approve_refused_list,
                approve_passed_list=approve_passed_list)

    return render_to_response('publish/publish_sheets.html', data)


@login_required
def PublishSheetDoneList(request):
    # 已完成 & 超时未审批 & 超时未发布的发布单
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
                    content['first_approver'] = sheet_history_obj.first_approver.username
                    content['first_approve_time'] = sheet_history_obj.first_approve_time
                    content['second_approver'] = sheet_history_obj.second_approver.username
                    content['second_approve_time'] = sheet_history_obj.second_approve_time
                    content['refuse_reason'] = sheet_history_obj.refuse_reason

    print content
    data = dict(code=errcode, msg=msg, content=content)
    return render_to_response('publish/publish_sheet_refusereason.html', data)


@login_required
def createPublishSheet(request):
    errcode = 0
    msg = 'ok'
    user = request.user
    ip = request.META['REMOTE_ADDR']
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
            print 'no project_info of this gogroup: ', project_name
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
            publishsheet_obj.approval_level = models.ApprovalLevel.objects.get(name='1')

        publishsheet_obj.save()
        asset_utils.logs(user.username, ip, 'create publish sheet', 'success')
        print '^^^^^save publishsheet_obj ok，id ----', publishsheet_obj.id

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
    ip = request.META['REMOTE_ADDR']
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
                asset_utils.logs(user.username, ip, 'delete publish sheet', 'success')
            else:
                errcode = 500
                msg = u'你不是创建人，不能删除'
        else:
            print 'no creator'
            publish_obj.delete()
            asset_utils.logs(user.username, ip, 'delete publish sheet', 'success')

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
            if publish.approval_level.name != '1':
                # 超时未审批
                publish.status = '6'
                publish.save()
        else:
            approve_level = publish.approval_level.name
            services_objs = publish.goservices.all().order_by('name')
            services_str = ', '.join(services_objs.values_list('name', flat=True))
            env = services_objs[0].get_env_display()
            gogroup_obj = services_objs[0].group
            level = publish.approval_level.get_name_display()

            tmp_dict = utils.serialize_instance(publish)
            if len(publish.sql) > 40:
                tmp_dict['sql'] = utils.cut_str(publish.sql, 40)
            if len(publish.consul_key) > 40:
                tmp_dict['consul_key'] = utils.cut_str(publish.consul_key, 40)

            # 判断单子状态，决定是否显示在我的审批页面
            if approve_level == '1':
                # 无需审批，不显示在审批页面
                pass
            elif approve_level == '2':
                # 一级审批的单子
                first_list = [owner.username for owner in publish.first_approver.all()]
                first_str = ', '.join(first_list)
                second_str = ''

                tmp_dict.update(
                    {'id': publish.id, 'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env,
                     'approve_level': approve_level, 'level': level, 'first_str': first_str,
                     'second_str': second_str, 'creator': publish.creator.username})

                if user.username in first_list:
                    if publish.status == '1':
                        tobe_approved_list.append(tmp_dict)
                    elif publish.status == '2':
                        approve_refused_list.append(tmp_dict)
                    elif publish.status == '6':
                        # 超时未审批
                        pass
                    else:
                        approve_passed_list.append(tmp_dict)

            else:
                # 二级审批的单子
                first_list = [owner.username for owner in publish.first_approver.all()]
                first_str = ', '.join(first_list)
                second_list = [owner.username for owner in publish.second_approver.all()]
                second_str = ', '.join(second_list)

                tmp_dict.update(
                    {'id': publish.id, 'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env,
                     'approve_level': approve_level, 'level': level, 'first_str': first_str,
                     'second_str': second_str, 'creator': publish.creator.username})

                if user.username in first_list:
                    if publish.status == '1':
                        tobe_approved_list.append(tmp_dict)
                    elif publish.status == '2':
                        approve_refused_list.append(tmp_dict)
                    elif publish.status == '6':
                        # 超时未审批
                        pass
                    else:
                        approve_passed_list.append(tmp_dict)

                elif user.username in second_list:
                    try:
                        history_obj = models.PublishApprovalHistory.objects.get(publish_sheet=publish)
                    except models.PublishApprovalHistory.DoesNotExist:
                        print '2----history not exist'
                    else:
                        if publish.status == '2':
                            if history_obj.approve_count == '2':
                                if history_obj.second_approver == user:
                                    approve_refused_list.append(tmp_dict)

                        if publish.status == '3':
                            if history_obj.approve_count == '1':
                                tobe_approved_list.append(tmp_dict)
                            else:
                                if history_obj.second_approver == user:
                                    approve_passed_list.append(tmp_dict)

    return render(request, 'approve/approve_list.html',
                  {'tobe_approved_list': tobe_approved_list, 'approve_refused_list': approve_refused_list,
                   'approve_passed_list': approve_passed_list})


@login_required
def ApproveInit(request):
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
        return render_to_response('approve/approve_sheet.html', data)


@login_required
def ApproveJudge(request):
    user = request.user
    ip = request.META['REMOTE_ADDR']
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
            asset_utils.logs(user.username, ip, 'first approve publish sheet', 'success')
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
            asset_utils.logs(user.username, ip, 'second approve publish sheet', 'success')

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def PublishSheetDetail(request):
    errcode = 0
    msg = 'ok'
    content = {}
    sheet_id = int(request.GET['sheet_id'])

    try:
        sheet_obj = models.PublishSheet.objects.get(id=sheet_id)
    except models.PublishSheet.DoesNotExist:
        errcode = 500
        msg = u'所选发布单不存在'
        print 'not exist'
    else:
        if sheet_obj.approval_level.name == '1':
            services_objs = sheet_obj.goservices.all().order_by('name')
            services_str = ', '.join(services_objs.values_list('name', flat=True))
            env = services_objs[0].get_env_display()
            gogroup_obj = services_objs[0].group
            level = sheet_obj.approval_level.get_name_display()
            approve_level = sheet_obj.approval_level.name

            content = utils.serialize_instance(sheet_obj)

            if len(sheet_obj.sql) > 40:
                content['sql'] = utils.cut_str(sheet_obj.sql, 40)
            if len(sheet_obj.consul_key) > 40:
                content['consul_key'] = utils.cut_str(sheet_obj.consul_key, 40)

            content.update({'id': sheet_obj.id, 'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env,
                            'approve_level': approve_level, 'level': level, 'creator': sheet_obj.creator.username})
        else:
            try:
                sheet_history_obj = models.PublishApprovalHistory.objects.get(publish_sheet=sheet_obj)
            except models.PublishApprovalHistory.DoesNotExist:
                print 'PublishSheetDetail---history not exist'
                services_objs = sheet_obj.goservices.all().order_by('name')
                services_str = ', '.join(services_objs.values_list('name', flat=True))
                env = services_objs[0].get_env_display()
                gogroup_obj = services_objs[0].group
                level = sheet_obj.approval_level.get_name_display()
                approve_level = sheet_obj.approval_level.name

                content = utils.serialize_instance(sheet_obj)

                if len(sheet_obj.sql) > 40:
                    content['sql'] = utils.cut_str(sheet_obj.sql, 40)
                if len(sheet_obj.consul_key) > 40:
                    content['consul_key'] = utils.cut_str(sheet_obj.consul_key, 40)

                content.update({'id': sheet_obj.id, 'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env,
                                'approve_level': approve_level, 'level': level, 'creator': sheet_obj.creator.username})
            else:
                services_objs = sheet_obj.goservices.all().order_by('name')
                services_str = ', '.join(services_objs.values_list('name', flat=True))
                env = services_objs[0].get_env_display()
                gogroup_obj = services_objs[0].group
                level = sheet_obj.approval_level.get_name_display()
                approve_level = sheet_obj.approval_level.name

                content = utils.serialize_instance(sheet_obj)

                if len(sheet_obj.sql) > 40:
                    content['sql'] = utils.cut_str(sheet_obj.sql, 40)
                if len(sheet_obj.consul_key) > 40:
                    content['consul_key'] = utils.cut_str(sheet_obj.consul_key, 40)

                content.update({'id': sheet_obj.id, 'gogroup': gogroup_obj.name, 'services_str': services_str, 'env': env,
                                 'approve_level': approve_level, 'level': level, 'creator': sheet_obj.creator.username})

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
    print '^^^^^^^^^^^^^^^'
    print content
    data = dict(code=errcode, msg=msg, content=content)
    return render_to_response('publish/publish_sheet_detail.html', data)


@login_required
def StartPublish(request):
    user = request.user
    ip = request.META['REMOTE_ADDR']
    sheet_id = int(request.POST['sheet_id'])
    errcode = 0
    msg = 'ok'
    try:
        publishsheet = models.PublishSheet.objects.get(id=sheet_id)
    except models.PublishSheet.DoesNotExist:
        errcode = 500
        msg = u'发布单不存在'
        data = dict(code=errcode, msg=msg)
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        try:
            userprofile = asset_models.UserProfile.objects.get(user=user)
        except asset_models.UserProfile.DoesNotExist:
            phone_number = ''
        else:
            phone_number = userprofile.phone_number

        goservices = publishsheet.goservices.all()
        goproject_name = goservices[0].group.name
        services = goservices.values_list('name', flat=True)
        env = goservices[0].env
        tower_url = publishsheet.tapd_url

        publish_ok = True

        Publish = asset_utils.goPublish(env)

        result = []
        for svc in services:
            rst = Publish.deployGo(goproject_name, svc, request.user.username, ip, tower_url, phone_number)
            result.extend(rst)

            # break once deploy failed
            if not asset_utils.get_service_status(svc):
                print("deploy %s failed" % svc)
                publish_ok = False
                break

        if publish_ok:
            publishsheet.status = '4'
            publishsheet.save()
            print 'publish ok'
            asset_utils.logs(user.username, ip, 'deploy publish sheet', 'success')
        else:
            print 'publish failed'
            asset_utils.logs(user.username, ip, 'deploy publish sheet', 'failed')

    data = dict(code=errcode, msg=msg)
    return HttpResponse(json.dumps(data), content_type='application/json')
