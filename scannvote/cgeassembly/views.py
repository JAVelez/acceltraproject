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
    """
    view that returns a list of assemblies to access
    """
    template_name = 'cgeassembly/assemblyindex.html'
    context_object_name = 'assemblies'

    def get_queryset(self):
        return Assembly.objects.order_by('-date')


class AssemblyDetailView(generic.DetailView):
    """
    view that returns the details of the selected assembly object
    """
    template_name = 'cgeassembly/assemblydetail.html'
    context_object_name = 'assembly'

    def get_queryset(self):
        return Assembly.objects.order_by('-date')


class MotionDetailView(generic.DetailView):
    """
    view that returns the details of the selected motion object
    """
    model = Motion
    template_name = 'cgeassembly/motiondetail.html'


class MotionResultsView(generic.DetailView):
    """
    motion to present the result of the currently selected motion
    """
    model = Motion
    template_name = 'cgeassembly/motionresults.html'


@login_required(login_url=settings.LOGIN_URL)
def vote(request, motion_id):
    """
    vote view only accessible if user is logged in will process their request to vote on a motion
    :param request: http request containing their vote choice
    :param motion_id: motion id that belongs to the motion being voted on
    :return: if successful, redirects to results page, if not, returns an appropriate error message
    """
    motion = get_object_or_404(Motion, pk=motion_id)
    student = base.Student.get_student_by_user(request.user)

    # case where a staff member has not open the motion to votes or is a past motion already voted on (archived)
    if motion.archived or not motion.voteable:
        return render(request, 'cgeassembly/motiondetail.html',
                      {'motion': motion, 'error_message': "Voting is not open at the moment", })

    # case where a student is not attending the assembly but the motion is voteable and not archived
    if not student.attending:
        return render(request, 'cgeassembly/motiondetail.html',
                      {'motion': motion, 'error_message': "You are not attending the assembly", })
    try:
        selected_choice = motion.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # case where the student didn't select a choice to vote on
        return render(request, 'cgeassembly/motiondetail.html', {'motion': motion, 'error_message': "You didn't select a choice.",})
    else:
        # case where the student successfully votes on the motion
        if models.create_vote(motion=motion, student=student):
            selected_choice.votes +=1
            selected_choice.save()
        else:
            # case where create_vote returns None and the vote is not processed
            # because the student has already cast their vote
            return render(request, 'cgeassembly/motiondetail.html',
                          {'motion': motion, 'error_message': "You have already cast your vote.",})
        return HttpResponseRedirect(reverse('cgeassembly:motionresults', args=(motion.id,)))


