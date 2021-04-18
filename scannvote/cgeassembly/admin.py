from django.db import models
from django.contrib import admin

from .models import Assembly, Interaction, Motion, Amendment, AgendaPoint


class AssemblyAdmin(admin.ModelAdmin):
    list_display = ['assembly_name', 'date', 'quorum']


class MotionAdmin(admin.ModelAdmin):
    # changeview
    fieldsets = [
        ('Required Fields', {'fields': ['assembly', 'motion_text', ]}),
        ('Ability to vote', {'fields': ['voteable']}),
        ('Date information', {'fields': ['date', 'archived']}),
    ]
    # changelistview
    list_display = ['motion_text', 'assembly', 'a_favor', 'en_contra', 'abstenido']
    list_filter = ['is_Amendment']


class AmendmentAdmin(admin.ModelAdmin):
    # changeview
    fieldsets = [
        ('Required Fields', {'fields': ['assembly', 'motion_amended', 'motion_text', ]}),
        ('Ability to vote', {'fields': ['voteable']}),
        ('Date information', {'fields': ['date', 'archived']}),
    ]
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
