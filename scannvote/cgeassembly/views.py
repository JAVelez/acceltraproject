from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import generic

from django.shortcuts import render
from .models import Motion, Choice
import scannvote.settings as settings


class IndexView(generic.ListView):
    template_name = 'cgeassembly/index.html'
    context_object_name = 'latest_motion_list'

    def get_queryset(self):
        return Motion.objects.order_by('-date')[:5]


class DetailView(generic.DetailView):
    model = Motion
    template_name = 'cgeassembly/detail.html'


class ResultsView(generic.DetailView):
    model = Motion
    template_name = 'cgeassembly/results.html'


@login_required(login_url=settings.LOGIN_URL)
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


