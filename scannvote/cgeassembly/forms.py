from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    student_id = forms.IntegerField(help_text='Required. Format: xxxxxxxxx')

    class Meta:
        model = User
        fields = ('username', 'student_id', 'password1', 'password2', )