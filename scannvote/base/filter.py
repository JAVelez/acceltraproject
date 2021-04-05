from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from .models import Student


class isPresentFilter(admin.SimpleListFilter):
    title = 'Students in Assembly'
    parameter_name = 'isPresent'
    default_value = ""

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        list_of_student = []
        options = ['false', 'true']
        queryset = Student.objects.all()
        for student in queryset:
            if student.is_present in options:
                list_of_student.append(
                    (str(student.is_present), student.is_present)
                )
                options.remove(student.is_present)
        return sorted(list_of_student, key=lambda tp: tp[1])

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        if self.value():
            return queryset.filter(is_present=self.value())
        return queryset

    def value(self):
        """
        Overriding this method will allow us to always have a default value.
        """
        value = super(isPresentFilter, self).value()
        if value is None:
            if self.default_value is None:
                # If there is at least one Stdent, return the first by name. Otherwise, None.
                first_student = Student.objects.order_by('user').first()
                value = None if first_student is None else first_student.student_id
                self.default_value = value
            else:
                value = self.default_value
        return str(value)
