from django.contrib import admin
from django.contrib.auth.models import User

from .models import Student


class StudentAdmin(admin.ModelAdmin):
    """
        admin model that allows administrator to create, edit and use students
        :param list_display: determines what parameters will be displayed in the screen
        :param list_filter: determines what parameters will filter the display
        :param actions: list of actions that will be available to the administrator
        :param fieldsets: Fields to be displayed when editing or creating a student
    """
    list_display = ('student_id', 'user', 'faculty', 'attending')
    list_filter = ('attending',)
    actions = ['make_false', ]
    fieldsets = [
        ('Required Fields', {'fields': ['student_id', 'user', 'faculty', ]}),
    ]

    def log_addition(self, *args):
        """
            method to remove adding action to recent actions display
        """
        return

    def log_change(self, *args):
        """
            method eliminate change actions from recent actions display
        """
        return

    def log_deletion(self, *args):
        """
            method eliminate delete actions from recent actions display
        """
        return

    def make_false(self, request, queryset):
        """
            method to change student attending status to false
            used to terminate current assembly
        """
        queryset.update(attending=False)
    make_false.short_description = 'Make students attending status false'


admin.site.register(Student, StudentAdmin)
