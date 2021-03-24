from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import base.models as base

# CGE focused models


class Assembly(models.Model):
    assembly_name = models.CharField(max_length=200, default="")
    date = models.DateTimeField('event date')
    quorum = models.IntegerField(default=0, editable=False)
    agenda = models.CharField(max_length=500, default="")
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.assembly_name

    def get_attendee_list(self):
        attendee_list = base.Student.objects.filter(attending=True)
        return attendee_list

    # def get_active_list(self):
    #     active_list = self.get_attendee_list().order_by('timestamp').distinct('student')
    #     return active_list

    def get_quorum_count(self):
        quorum = self.get_attendee_list().count()
        return quorum

    def update_quorum(self):
        self.quorum = self.get_quorum_count()

    def get_prev_assembly(self):
        qs = Assembly.objects.order_by('-date')
        if len(qs) == 1:
            return None
        else:
            return qs[1]

    class Meta:
        verbose_name_plural = "Assemblies"

# TODO adaptar método para assembly y motion y ammendment lmao
@receiver(post_save, sender=Assembly)
def update_assembly_archive(sender, instance, created, **kwargs):
    if created:
        assembly_to_archive = instance.get_prev_assembly()
        if assembly_to_archive:
            assembly_to_archive.archived = True
            assembly_to_archive.save()


class Interaction(models.Model):
    # id = models.BigIntegerField(primary_key=True)
    student = models.ForeignKey(base.Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField('date interacted', default=timezone.now)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE)

    def count_student_interactions(self, student_id):
        count = Interaction.objects.filter(student_id=student_id).count()
        return count


@receiver(post_save, sender=Interaction)
def update_attending(sender, instance, created, **kwargs):
    if created:
        # % 2 == 0 represents even interactions
        if instance.count_student_interactions(instance.student_id) % 2 == 0:
            instance.student.attending = False
        else:
            instance.student.attending = True
        instance.student.save()


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
