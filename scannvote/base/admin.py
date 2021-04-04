from django.contrib import admin
from django.contrib.auth.models import User

from .models import Student, Quorum
from .filter import isPresentFilter


class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'faculty', 'is_present')
    # list_display = ('student_id', 'first_name', 'user', 'faculty')
    # list_display = ('student_id', 'first_name', 'last_name', 'faculty')
    list_filter = (isPresentFilter,)


class QuorumAdmin(admin.ModelAdmin):
    list_display = ('users', 'isPresent')


admin.site.register(Student, StudentAdmin)
admin.site.register(Quorum, QuorumAdmin)
