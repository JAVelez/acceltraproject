from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from django.shortcuts import render
from .models import Motion, Assembly, Vote, Interaction
import scannvote.settings as settings
import base.models as base
from . import models
from .forms import EntryForm

# motion choices
A_FAVOR = '0'
EN_CONTRA = '1'
ABSTENIDO = '2'


class AssemblyIndexView(generic.ListView):
    """
    view that returns a list of assemblies to access
    """
    template_name = 'cgeassembly/assemblyindex.html'
    context_object_name = 'assemblies'

    def get_queryset(self):
        return Assembly.objects.order_by('-date')


def AssemblyDetailView(request, pk):
    """
    view that returns the details of the selected assembly object
    """
    assembly = get_object_or_404(Assembly, pk=pk)
    motion_set = Motion.objects.filter(assembly=assembly, amendment=None)
    return render(request, 'cgeassembly/assemblydetail.html',
                  {'assembly': assembly, 'motion_set': motion_set, 'status_code': '200'})


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
                      {'motion': motion, 'error_message': "Voting is not open at the moment",
                       'status_code': '200', 'code': '0'})

    # case where a student is not attending the assembly but the motion is voteable and not archived
    if not student.attending:
        return render(request, 'cgeassembly/motiondetail.html',
                      {'motion': motion, 'error_message': "You are not attending the assembly",
                       'status_code': '200', 'code': '1'})

    try:
        selected_choice = request.POST['choice']
    except:
        return render(request, 'cgeassembly/motiondetail.html', {'motion': motion,
                                                                 'error_message': "You didn't select a choice.",
                                                                 'status_code': '200', 'code': '2'})

    else:
        # case where the student successfully votes on the motion
        if models.create_vote(motion=motion, student=student):
            if selected_choice is A_FAVOR:
                motion.a_favor += 1
            elif selected_choice is EN_CONTRA:
                motion.en_contra += 1
            else:
                motion.abstenido += 1
            motion.save()
        else:
            # case where create_vote returns None and the vote is not processed
            # because the student has already cast their vote
            return render(request, 'cgeassembly/motiondetail.html',
                          {'motion': motion, 'error_message': "You have already cast your vote.",
                           'status_code': '200', 'code': '3'})
        return HttpResponseRedirect(reverse('cgeassembly:motionresults', args=(motion.id,)))


# TODO only staff members can access these url's
@login_required(login_url=settings.LOGIN_URL)
def scanner(request):
    """
    scanner view only accessible if admin is logged in and will process their request to scan a student id card
    :param request: http request containing their student_id
    :return: if successful, redirects to scanner page, if not, returns an appropriate error message
    """
    if not request.user.is_staff and not request.user.is_superuser:
        return render(request, 'cgeassembly/scanner.html', {'status_code': '200', 'code': '3',
                                                            'error_message': 'The user does not have the required permissions'})
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            student_id = form.clean_student_id()
            student = base.Student.get_student_by_student_id(student_id)
            assembly = Assembly.get_current_assembly()
            if student and assembly:
                Interaction.objects.create(student=student, assembly=assembly)
                if Interaction.count_student_interactions(student.id) % 2 - 1 == 0:
                    code = '0'  # started attending
                else:
                    code = '1'  # stopped attending
                return render(request, 'cgeassembly/scanner.html', {'form': EntryForm(),
                                                                    'status_code': '200', 'code': code})
            else:
                return render(request, 'cgeassembly/scanner.html', {'form': form,
                                                                    'status_code': '200', 'code': '2',
                                                                    'error_message': 'Student id is not in the database.'})
    else:
        form = EntryForm()
    return render(request, 'cgeassembly/scanner.html', {'form': form, 'status_code': '200'})

