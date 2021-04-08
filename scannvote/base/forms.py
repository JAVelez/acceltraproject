from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from .models import Student

# validator to parse student id
numeric = RegexValidator(r'\d{9}', 'Only digit characters.')


class SignUpForm(UserCreationForm):
    """
    form that overrides Django's user creation form to include the requirement of student id
    """
    error_messages = {
        'student_id_taken': 'Student ID already has an account.',
        'password_mismatch': 'Passwords do not match.'
    }

    student_id = forms.CharField(help_text='Required. Format: xxxxxxxxx',
                                 validators=[MaxLengthValidator(limit_value=9),
                                             MinLengthValidator(limit_value=9),
                                             numeric])

    def clean_student_id(self):
        """
        method to be called when cleaning form input within django's core functionalities
        verifies if student id is taken
        :return: student id number
        """
        student_id = self.data.get("student_id").strip()
        if Student.student_exists(student_id):
            raise ValidationError(
                self.error_messages['student_id_taken'],
            )
        return student_id

    class Meta:
        model = User
        fields = ('username', 'student_id', 'password1', 'password2',)


class LoginForm(AuthenticationForm):
    pass
