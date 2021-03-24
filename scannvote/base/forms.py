from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from .models import Student


numeric = RegexValidator(r'\d{9}', 'Only digit characters.')


class SignUpForm(UserCreationForm):
    error_messages = {
        'student_id_taken': 'Student ID already has an account.',
        'password_mismatch': 'Passwords do not match.'
    }

    student_id = forms.CharField(help_text='Required. Format: xxxxxxxxx',
                                 validators=[MaxLengthValidator(limit_value=9),
                                             MinLengthValidator(limit_value=9),
                                             numeric])

    def clean_student_id(self):
        student_id = self.data.get("student_id")
        if Student.student_exists(Student, student_id):
            raise ValidationError(
                self.error_messages['student_id_taken'],
            )
        return student_id

    class Meta:
        model = User
        fields = ('username', 'student_id', 'password1', 'password2',)


class LoginForm(AuthenticationForm):
    pass
