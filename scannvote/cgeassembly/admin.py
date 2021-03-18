from django.contrib import admin

from .models import Assembly, Motion, Choice


class ChoicesInLine(admin.TabularInline):
    model = Choice
    extra = 3


class MotionAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Required Fields', {'fields': ['assembly', 'motion_text', ]}),
        ('Ability to vote', {'fields': ['current_motion', 'open_to_vote']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
    inlines = [ChoicesInLine]
    list_display = ['motion_text', 'pub_date']


class AssemblyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Assembly, AssemblyAdmin)
admin.site.register(Motion, MotionAdmin)
