from django.db import models
from django.utils import timezone
import base.models as base

# CGE focused models


class Assembly(models.Model):
    assembly_name = models.CharField(max_length=200, default="")
    date = models.DateTimeField('event date')
    quorum = models.IntegerField(default=0, editable=False)
    agenda = models.CharField(max_length=500, default="")

    def __str__(self):
        return self.assembly_name

    def get_attendee_list(self):
        attendee_list = Interaction.objects.filter(assembly=self, attending=True)
        return attendee_list

    def get_active_list(self):
        active_list = self.get_attendee_list().order_by('timestamp').distinct('student')
        return active_list

    def get_quorum_count(self):
        quorum = self.get_active_list().count()
        return quorum

    class Meta:
        verbose_name_plural = "Assemblies"


class Interaction(models.Model):
    student = models.OneToOneField(base.Student, on_delete=models.CASCADE, primary_key=True)
    timestamp = models.DateTimeField('date interacted', default=timezone.now)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)
    # TODO consider moving this attribute to student model and updating according
    #  to latest daily interaction interaction
    attending = models.BooleanField()

    def update_quorum(self):
        self.assembly.quorum = Assembly.get_quorum_count()


class Motion(models.Model):
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, default="")
    motion_text = models.CharField(max_length=500)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    # 1 = true; 0 = false
    current_motion = models.IntegerField(default=1)
    open_to_vote = models.IntegerField(default=0)

    # # alt to manual opening and closing
    # open_date = models.DateTimeField('date opened to vote')
    # closing_date = models.DateTimeField('date closed to vote')

    def __str__(self):
        return self.motion_text


class Choice(models.Model):
    choices = {
        ('a favor', 'a favor'),
        ('en contra', 'en contra'),
        ('abstenido', 'abstenido'),
    }
    motion = models.ForeignKey(Motion, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200, choices=choices)
    votes = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return self.choice_text
