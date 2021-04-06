from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import SignUpForm, LoginForm
import scannvote.settings as settings

# Create your views here.


@login_required(login_url=settings.LOGIN_URL)
def home(request):
    return render(request, 'base/home.html')


def signup(request):
    """

    :param request: http request with form attached to it
    :return: if successful, home page showing student details; if not, signup page to try again
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            student_id = form.clean_student_id()
            user = form.save()

            # load the profile instance created by the signal
            user.refresh_from_db()

            # assign student id to user's student one to one relation and save to db
            user.student.student_id = student_id
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = SignUpForm()
    return render(request, 'base/signup.html', {'form': form})


def login_student(request):
    """

    :param request: http request with login form
    :return: if successful, home page showing student details; if not, login page to try again
    """
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
        else:
            return render(request, 'base/login_failed.html', {'form': LoginForm()})
    form = LoginForm()
    return render(request, 'base/login.html', {'form': form})


def logout_student(request):
    """
    method to remove student from active session
    :param request: http request
    :return: home page with no user session active which in turn returns to the login page
    """
    logout(request)
    return HttpResponseRedirect(reverse('home'))

