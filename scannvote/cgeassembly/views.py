from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from .forms import SignUpForm
from .models import Motion, Choice, Assembly, Student


class IndexView(generic.ListView):
    template_name = 'cgeassembly/index.html'
    context_object_name = 'latest_motion_list'

    def get_queryset(self):
        return Motion.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Motion
    template_name = 'cgeassembly/detail.html'


class ResultsView(generic.DetailView):
    model = Motion
    template_name = 'cgeassembly/results.html'


def vote(request, motion_id):
    motion = get_object_or_404(Motion, pk = motion_id)
    try:
        selected_choice = motion.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'cgeassembly/detail.html', {'motion': motion, 'error_message': "You didn't select a choice.",})
    else:
        selected_choice.votes +=1
        selected_choice.save()
        return HttpResponseRedirect(reverse('cgeassembly:results', args=(motion.id,)))


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
            return HttpResponseRedirect(reverse('cgeassembly:student', args=(user,)))
    else:
        form = SignUpForm()
    return render(request, 'cgeassembly/signup.html', {'form': form})


class StudentView(generic.DetailView):
    model = Student
    template_name = 'cgeassembly/student.html'


