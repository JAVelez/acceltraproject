from django.contrib import admin

from .models import Assembly, Interaction, Motion, Amendment


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
    list_display = ['motion_text', 'date', 'assembly']


class AmendmentAdmin(admin.ModelAdmin):
    # changeview
    fieldsets = [
        ('Required Fields', {'fields': ['assembly', 'motion_amended', 'motion_text', ]}),
        ('Ability to vote', {'fields': ['voteable']}),
        ('Date information', {'fields': ['date', 'archived']}),
    ]
    # changelistview
    list_display = ['motion_text', 'date', 'assembly']


class InteractionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Required Fields', {'fields': ['student', 'timestamp', 'assembly']}),
    ]

    list_display = ['student', 'timestamp', 'assembly']


admin.site.register(Assembly, AssemblyAdmin)
admin.site.register(Motion, MotionAdmin)
admin.site.register(Amendment, AmendmentAdmin)
admin.site.register(Interaction, InteractionAdmin)
