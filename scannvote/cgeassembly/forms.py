from django import forms

from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator
import base.forms as baseform
import base.models as base
from .models import Interaction


class EntryForm(forms.ModelForm):
    """
    form that processes a staff's request to scan a student_id card
    """
    error_messages = {
        'student_id_does_not_exist': 'Student ID is not registered in the database.',
    }

    student_id = forms.CharField(help_text='Required. Format: xxxxxxxxx',
                                 validators=[MaxLengthValidator(limit_value=9),
                                             MinLengthValidator(limit_value=9),
                                             baseform.numeric])

    def clean_student_id(self):
        """
        method to be called when cleaning form input within django's core functionalities
        verifies if student id exists in the database
        :return: student id number
        """
        student_id = self.data.get("student_id").strip()
        if not base.Student.student_exists(student_id):
            raise ValidationError(
                self.error_messages['student_id_does_not_exist'],
            )
        return student_id

    class Meta:
        model = Interaction
        fields = ('student_id', )