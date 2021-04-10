from django.contrib import admin
from django.contrib.auth.models import User

from .models import Student
from .filter import isPresentFilter


#@admin.make_false(description='Make students attending status false')
# def make_false(modeladmin, request, queryset):
#     queryset.update(attending=False)
#
#
# make_false.short_description = 'Make students attending status false'


class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'faculty', 'attending')
    #list_filter = (isPresentFilter,)
    list_filter = ('attending',)
    actions = ['make_false', ]

    def make_false(self, request, queryset):
        queryset.update(attending=False)
    make_false.short_description = 'Make students attending status false'


admin.site.register(Student, StudentAdmin)
