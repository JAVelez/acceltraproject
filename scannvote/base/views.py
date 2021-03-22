from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import SignUpForm, LoginForm

# Create your views here.


@login_required()
def home(request):
    return render(request, 'base/home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.student.student_id = form.cleaned_data.get('student_id')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse('home:home'))
    else:
        form = SignUpForm()
    return render(request, 'base/signup.html', {'form': form})


def login_student(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        login(request, user)
        return HttpResponseRedirect(reverse('home:home'))
    else:
        form = LoginForm()
    return render(request, 'base/login.html', {'form': form})


def logout_student(request):
    logout(request)
    return HttpResponseRedirect(reverse('home:home'))

