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

    @staticmethod
    def get_attendee_list():
        attendee_list = base.Student.objects.filter(attending=True)
        return attendee_list

    def get_quorum_count(self):
        quorum = self.get_attendee_list().count()
        return quorum

    def update_quorum(self):
        self.quorum = self.get_quorum_count()

    class Meta:
        verbose_name_plural = "Assemblies"


class Interaction(models.Model):
    student = models.ForeignKey(base.Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField('date interacted', default=timezone.now)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, limit_choices_to={'archived': False})

    @staticmethod
    def count_student_interactions(student_id):
        count = Interaction.objects.filter(student_id=student_id).count()
        return count


@receiver(post_save, sender=Interaction)
def update_attending(sender, instance, created, **kwargs):
    if created:
        # % 2 == 0 represents even interactions :: leaving the assembly
        if instance.count_student_interactions(instance.student_id) % 2 == 0:
            instance.student.attending = False
        else:
            instance.student.attending = True
        instance.student.save()


class Motion(models.Model):
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, limit_choices_to={'archived': False})
    motion_text = models.CharField(max_length=500)
    date = models.DateTimeField('date published', default=timezone.now)
    archived = models.BooleanField(default=False)
    voteable = models.BooleanField(default=False)

    # # alt to manual opening and closing
    # open_date = models.DateTimeField('date opened to vote')
    # closing_date = models.DateTimeField('date closed to vote')

    def __str__(self):
        return self.motion_text[:30] + "..."

# TODO crear modelo "vote" con foreign keys de user y motion :)


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


class Amendment(Motion):
    motion_amended = models.ForeignKey(Motion, on_delete=models.CASCADE,
                                       related_name='original_motion',
                                       limit_choices_to={'archived': False})


def get_prev_model(model):
    qs = model.objects.order_by('-date')
    if len(qs) == 1:
        return None
    else:
        return qs[1]


@receiver(post_save, sender=Motion)
@receiver(post_save, sender=Assembly)
def update_model_archive(sender, instance, created, **kwargs):
    if created:
        model_to_archive = get_prev_model(sender)
        if model_to_archive:
            model_to_archive.archived = True
            model_to_archive.save()
