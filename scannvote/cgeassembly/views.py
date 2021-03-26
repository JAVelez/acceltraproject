from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from django.shortcuts import render
from .models import Motion, Choice, Assembly, Vote
import scannvote.settings as settings
import base.models as base
from . import models


class AssemblyIndexView(generic.ListView):
    template_name = 'cgeassembly/assemblyindex.html'
    context_object_name = 'assemblies'

    def get_queryset(self):
        return Assembly.objects.order_by('-date')


class AssemblyDetailView(generic.DetailView):
    template_name = 'cgeassembly/assemblydetail.html'
    context_object_name = 'assembly'

    def get_queryset(self):
        return Assembly.objects.order_by('-date')


class MotionIndexView(generic.ListView):
    template_name = 'cgeassembly/motionindex.html'
    context_object_name = 'latest_motion_list'

    def get_queryset(self):
        return Motion.objects.order_by('-date')[:5]


class MotionDetailView(generic.DetailView):
    model = Motion
    template_name = 'cgeassembly/motiondetail.html'


class MotionResultsView(generic.DetailView):
    model = Motion
    template_name = 'cgeassembly/motionresults.html'
    # TODO hide vote results if voteable == True


@login_required(login_url=settings.LOGIN_URL)
def vote(request, motion_id):
    motion = get_object_or_404(Motion, pk=motion_id)
    student = base.Student.get_student_by_user(request.user)
    if motion.archived or not motion.voteable:
        # code should never be reachable and stopped at the form level
        return render(request, 'cgeassembly/motiondetail.html',
                      {'motion': motion, 'error_message': "Voting is not open at the moment", })
    if not student.attending:
        return render(request, 'cgeassembly/motiondetail.html',
                      {'motion': motion, 'error_message': "You are not attending the assembly", })
    try:
        selected_choice = motion.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'cgeassembly/motiondetail.html', {'motion': motion, 'error_message': "You didn't select a choice.",})
    else:
        if models.create_vote(motion=motion, student=student):
            selected_choice.votes +=1
            selected_choice.save()
        else:
            return render(request, 'cgeassembly/motiondetail.html', {'motion': motion, 'error_message': "You have already cast your vote.",})
        return HttpResponseRedirect(reverse('cgeassembly:motionresults', args=(motion.id,)))


