# coding: utf-8

from django.db import models
from django.contrib.auth.models import User
from asset.models import gogroup


class MailGroup(models.Model):
    email = models.CharField(max_length=255)
    name = models.CharField(max_length=64, blank=True, null=True)

    def __unicode__(self):
        return self.email

    class Meta:
        verbose_name = u"邮件组"
        verbose_name_plural = verbose_name


class ProjectInfo(models.Model):
    group = models.ForeignKey(gogroup)
    owner = models.ManyToManyField(User, verbose_name=u'负责人', related_name='project_owner')
    mail_group = models.ManyToManyField(MailGroup, verbose_name=u'邮件组', related_name='project_mail_group')
    first_approver = models.ManyToManyField(User, verbose_name=u'一级审批人', related_name='project_first_level_approver')
    second_approver = models.ManyToManyField(User, verbose_name=u'二级审批人', related_name='project_second_level_approver')

    def __unicode__(self):
        return u'项目 : ' + self.group.name

    class Meta:
        verbose_name = u"项目初始化"
        verbose_name_plural = verbose_name


class ApprovalLevel(models.Model):
    LEVEL = (
        ('1', u'无需审批'),
        ('2', u'一级审批'),
        ('3', u'二级审批'),
    )
    name = models.CharField(choices=LEVEL, max_length=32, verbose_name=u"审批级别", default='1')

    def __unicode__(self):
        return self.get_name_display()

    class Meta:
        verbose_name = u"审批级别"
        verbose_name_plural = verbose_name


class TimeSlot(models.Model):
    DAY = (
        ('1', u'周一'),
        ('2', u'周二'),
        ('3', u'周三'),
        ('4', u'周四'),
        ('5', u'周五'),
        ('6', u'周六'),
        ('7', u'周日'),
    )
    project_info = models.ForeignKey(ProjectInfo)
    start_of_week = models.CharField(choices=DAY, max_length=32, verbose_name=u"起始", default='1')
    end_of_week = models.CharField(choices=DAY, max_length=32, verbose_name=u"截止", default='7')
    start_time = models.CharField(verbose_name=u'开始时间点', max_length=32, blank=True, null=True)
    end_time = models.CharField(verbose_name=u'结束时间点', max_length=32, blank=True, null=True)
    approval_level = models.ForeignKey(ApprovalLevel)

    def __unicode__(self):
        return u'时间段 : ' + self.project_info.group.name

    class Meta:
        verbose_name = u"时间段"
        verbose_name_plural = verbose_name


class Festival(models.Model):
    name = models.CharField(max_length=32, verbose_name=u"节日名称")
    start_day = models.DateField('日期')
    end_day = models.DateField('日期', null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = u"节假日"
        verbose_name_plural = verbose_name
