from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator
from .models import Student

# validator to parse student id
numeric = RegexValidator(r'\d{9}', 'Only digit characters.')
special_characters = ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', ',', '.', '/', '?', '"', ':', ';',
                      '{', '}', '|', '<', '>', '-', '+', '=']

user_error_messages = {'un_lt': 'Username length must be greater than or equal to 8.',
                       'un_gt': 'Username length must be less than or equal to 16.',
                       'pw_lt': 'Password length must be greater than or equal to 8.',
                       'pw_gt': 'Password length must be less than or equal to 24.',
                       'pw_upper': 'Password must contain an uppercase letter.',
                       'pw_lower': 'Password must contain a lowercase letter.',
                       'pw_digit': 'Password must contain a digit.',
                       'pw_sc': 'Password must contain a special character.'
                       }


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

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 8:
            raise ValidationError(user_error_messages['un_lt'],)

        if len(username) > 16:
            raise ValidationError(user_error_messages['un_gt'],)

        return username

    def clean_password1(self):
        pw = self.data['password1']

        if len(pw) < 8:
            raise ValidationError(user_error_messages['pw_lt'],)

        if len(pw) > 24:
            raise ValidationError(user_error_messages['pw_gt'],)

        if not hasUpper(pw):
            raise ValidationError(user_error_messages['pw_upper'],)

        if not hasLower(pw):
            raise ValidationError(user_error_messages['pw_lower'],)

        if not hasDigit(pw):
            raise ValidationError(user_error_messages['pw_digit'],)

        if not hasSpecialchar(pw):
            raise ValidationError(user_error_messages['pw_sc'],)
        return pw

    class Meta:
        model = User
        fields = ('username', 'student_id', 'password1', 'password2',)


def hasUpper(inputString):
    return any(char.isupper() for char in inputString)


def hasLower(inputString):
    return any(char.islower() for char in inputString)


def hasDigit(inputString):
    return any(char.isdigit() for char in inputString)


def hasSpecialchar(inputString):
    for s in special_characters:
        if inputString.__contains__(s):
            return True

    return False

class LoginForm(AuthenticationForm):
    pass
