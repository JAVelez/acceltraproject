from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinLengthValidator, RegexValidator


numeric = RegexValidator(r'\d{9}', 'Only digit characters.')


class SignUpForm(UserCreationForm):
    student_id = forms.CharField(help_text='Required. Format: xxxxxxxxx',
                                 validators=[MaxLengthValidator(limit_value=9),
                                             MinLengthValidator(limit_value=9),
                                             numeric])

    class Meta:
        model = User
        fields = ('username', 'student_id', 'password1', 'password2',)


class LoginForm(AuthenticationForm):
    pass
