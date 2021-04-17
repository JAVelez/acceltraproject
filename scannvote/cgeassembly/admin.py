from django.db import models
from django.contrib import admin

from .models import Assembly, Choice, Interaction, Motion, Amendment, AgendaPoint
#from base.models import Student
import base.models as base


# def turn_off(modeladmin, request, queryset):
#     queryset.update(archived=True)
# turn_off.short_description = "Archive Everything"


#admin.site.add_action(turn_off)
# def make_assembly_archived(modeladmin, request, queryset):
#     queryset.update(archived=True)
# make_assembly_archived.short_description = 'Archive selected assembly(s)'


class AssemblyAdmin(admin.ModelAdmin):
    list_display = ['assembly_name', 'date', 'quorum']  # 'current_point']
    list_filter = ['archived']
    actions = ['make_assembly_archived', 'make_current', 'turn_off']

    def make_assembly_archived(self, request, queryset):
        queryset.update(archived=True)
    make_assembly_archived.short_description = "Archive selected assembly(s)"

    def make_current(self, request, queryset):
        queryset.update(current_assembly=True)
    make_current.short_description = "Make assembly current"

    def turn_off(self, request, queryset):
        queryset.update(archived=True)
        queryset.update(current_assembly=False)

        queryset1 = base.Student.objects.all()
        #for student in queryset:
        queryset1.update(attending=False)

        queryset2 = AgendaPoint.objects.all()
        #for Assembly.current_assembly in Assembly:
        #if AgendaPoint.assembly == Assembly.assembly_name:  # and Assembly.current_assembly == True:
        queryset2.update(current_point=False)
        queryset2.update(archived=True)

        queryset3 = Motion.objects.all()
        queryset3.update(voteable=False)
        queryset3.update(archived=True)

        queryset4 = Amendment.objects.all()
        queryset4.update(archived=True)
    turn_off.short_description = "Turn off assembly"


class ChoicesInLine(admin.TabularInline):
    model = Choice
#    extra = 3


class MotionAdmin(admin.ModelAdmin):
    # changeview
    fieldsets = [
        ('Required Fields', {'fields': ['assembly', 'motion_text', ]}),
        ('Ability to vote', {'fields': ['votable']}),
        ('Date information', {'fields': ['date', 'archived']}),
    ]
    inlines = [ChoicesInLine]

    # result_yes = models.IntegerField(default=0)
    # result_no = models.IntegerField(default=0)
    # result_abstain = models.IntegerField(default=0)
    # queryset = Choice.objects.all()

    # for Choice.choice_text in queryset:
    #     if Choice.choice_text == "a favor":
    #         result_yes = Choice.votes
    #     elif Choice.choice_text == "en contra":
    #         result_no = Choice.votes
    #     else:
    #         result_abstain = Choice.votes

    #votes = ChoicesInLine.model.votes

    list_display = ['motion_text', 'date', 'assembly',]# result_yes, result_no, result_abstain]
    list_filter = ['assembly', 'archived',]
    actions = ['make_motion_archived', 'make_motion_votable']

    def make_motion_archived(self, request, queryset):
        queryset.update(archived=True)
    make_motion_archived.short_description = "Archive selected motion(s)"

    def make_motion_votable(self, request, queryset):
        queryset.update(votable=True)
    make_motion_votable.short_description = "Allow motion to be votable"


class AmendmentAdmin(admin.ModelAdmin):
    # changeview
    fieldsets = [
        ('Required Fields', {'fields': ['assembly', 'motion_amended', 'motion_text', ]}),
        ('Ability to vote', {'fields': ['votable']}),
        ('Date information', {'fields': ['date', 'archived']}),
    ]
    inlines = [ChoicesInLine]
    # changelistview
    list_display = ['motion_text', 'date', 'assembly']
    list_filter = ['archived']
    actions = ['make_amendment_archived', ]

    def make_amendment_archived(self, request, queryset):
        queryset.update(archived=True)
    make_amendment_archived.short_description = "Archive selected amendment(s)"


class InteractionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Required Fields', {'fields': ['student', 'timestamp', 'assembly']}),
    ]

    list_display = ['student', 'timestamp', 'assembly']


class AgendaAdmin(admin.ModelAdmin):
    list_display = ['assembly', 'agenda_point', 'current_point']
    list_filter = ('assembly', 'archived')
    actions = ['make_false', 'make_true', 'make_agenda_point_archived', ]

    def make_false(self, request, queryset):
        queryset.update(current_point=False)
    make_false.short_description = 'Turn off agenda point(s)'

    def make_true(self, request, queryset):
        queryset.update(current_point=True)
    make_true.short_description = 'Turn on agenda point(s)'

    def make_agenda_point_archived(self, request, queryset):
        queryset.update(archived=True)
    make_agenda_point_archived.short_description = 'Archive selected agenda(s)'


admin.site.register(Assembly, AssemblyAdmin)
admin.site.register(Motion, MotionAdmin)
admin.site.register(Amendment, AmendmentAdmin)
admin.site.register(Interaction, InteractionAdmin)
admin.site.register(AgendaPoint, AgendaAdmin)
