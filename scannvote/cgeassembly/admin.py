from django.contrib import admin

from .models import Assembly, Motion, Choice, Interaction


class ChoicesInLine(admin.TabularInline):
    model = Choice
    extra = 3


class MotionAdmin(admin.ModelAdmin):
    # changeview
    fieldsets = [
        ('Required Fields', {'fields': ['assembly', 'motion_text', ]}),
        ('Ability to vote', {'fields': ['current_motion', 'open_to_vote']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
    inlines = [ChoicesInLine]
    # changelistview
    list_display = ['motion_text', 'pub_date']


class AssemblyAdmin(admin.ModelAdmin):
    list_display = ['assembly_name', 'date', 'quorum']


class InteractionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Required Fields', {'fields': ['student', 'timestamp', 'assembly']}),
    ]

    list_display = ['student', 'timestamp', 'assembly']

    # def assembly_options(self, obj):
    #     return obj
    #
    # assembly_options.admin_order_field = ''


admin.site.register(Motion, MotionAdmin)
admin.site.register(Assembly, AssemblyAdmin)
admin.site.register(Interaction, InteractionAdmin)
