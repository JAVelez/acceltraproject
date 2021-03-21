from django.contrib.auth import login, authenticate
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from .forms import SignUpForm
from .models import Student

# Create your views here.


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
            return HttpResponseRedirect(reverse('base:student', args=(user,)))
    else:
        form = SignUpForm()
    return render(request, 'base/signup.html', {'form': form})


class StudentView(generic.DetailView):
    model = Student
    template_name = 'base/student.html'
