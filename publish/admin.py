from django.contrib import admin
from publish.models import *


class MailGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ['name', 'email']


class ProjectInfoAdmin(admin.ModelAdmin):
    fields = ['group', 'owner', 'mail_group']
    list_display = ('group', 'get_mail_groups', 'get_owners')
    filter_horizontal = ('owner', 'mail_group')

    def get_mail_groups(self, obj):
        return "\n".join([p.name for p in obj.mail_group.all()])

    def get_owners(self, obj):
        return "\n".join([p.username for p in obj.owner.all()])


class ApprovalLevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']


class TimeSlotLevelAdmin(admin.ModelAdmin):
    list_display = ('start_of_week', 'end_of_week', 'start_time', 'end_time', 'approval_level')
    search_fields = ['approval_level']


class FestivalAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_day', 'end_day')
    search_fields = ['name', 'start_day', 'end_day']


admin.site.register(MailGroup, MailGroupAdmin)
admin.site.register(ProjectInfo, ProjectInfoAdmin)
admin.site.register(ApprovalLevel, ApprovalLevelAdmin)
admin.site.register(TimeSlotLevel, TimeSlotLevelAdmin)
admin.site.register(Festival, FestivalAdmin)
