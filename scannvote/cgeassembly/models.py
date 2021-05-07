from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import base.models as base

# CGE focused models


class Assembly(models.Model):
    def date_validation(value):
        """
        method that activates a validation error when a past event date is selected in the creation of assembly
        """
        today = date.today()
        if value < today:
            raise ValidationError('Please select a current or future date.')
    """
    model to add student values not found in Django's user model
    :param assembly_name: assembly name
    :param date: date representing when will the assembly be held on
    :param quorum: attendee count
    :param agenda: optional text area to present students with the assembly's agenda
    :param arhcived: once it conlcudes, archived = True (representing past assemblies)
    """
    assembly_name = models.CharField(max_length=200, default="")
    date = models.DateTimeField('pub date', editable=False, default=timezone.now)
    event_date = models.DateField('event date', default=timezone.now, validators=[date_validation])
    quorum = models.IntegerField(default=0, editable=False)
    agenda = models.TextField(max_length=1000, default="N/A")
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.assembly_name

    @staticmethod
    def get_attendee_list():
        """
        helper method to return complete attendee list
        :return: list containing every student model with attending = True
        """
        attendee_list = base.Student.objects.filter(attending=True)
        return attendee_list

    def get_quorum_count(self):
        """
        helper method to apply count aggregate to get_attendee_list()
        :return: int value representing quanitity of students attending the assembly
        """
        quorum = self.get_attendee_list().count()
        return quorum

    def update_quorum(self):
        """
        method to update the assembly's quorum; is called any time an interaction is created to update automatically
        whenever a student enters or leaves the assembly
        :return: n/a
        """
        self.quorum = self.get_quorum_count()

    @staticmethod
    def get_current_assembly():
        return Assembly.objects.filter(archived=False).first()

    class Meta:
        verbose_name_plural = "Assemblies"


class Interaction(models.Model):
    """
    model to represent whenever a student enters or leaves an assembly
    :param student: foreign key to the related student
    :param timestamp: when did it occur
    :param assembly: foreign key to the related assembly
    """
    student = models.ForeignKey(base.Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField('date interacted', default=timezone.now)
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, limit_choices_to={'archived': False})

    @staticmethod
    def count_student_interactions(student_pk):
        """
        helper method to return the amount of times a student has passed by the scanning station
        :param student_id: student id
        :return: quantity of student interactions in that assembly
        """
        current_assembly = Assembly.objects.get(archived=False)
        count = Interaction.objects.filter(student_id=student_pk, assembly=current_assembly).count()
        return count


@receiver(post_save, sender=Interaction)
def update_attending(sender, instance, created, **kwargs):
    """
    method that updates the attending value of a student whenever an interaction
    is created/student scans their student id
    :param sender: Interaction model
    :param instance: Interaction object
    :param created: successful creation of interaction object in db
    :param kwargs:
    :return: n/a
    """
    if created:
        # % 2 == 0 represents even interactions :: leaving the assembly
        if instance.count_student_interactions(instance.student_id) % 2 == 0:
            instance.student.attending = False
            instance.assembly.quorum = instance.assembly.quorum - 1
        else:
            instance.student.attending = True
            instance.assembly.quorum = instance.assembly.quorum + 1
        instance.student.save()
        instance.assembly.save()


class Motion(models.Model):
    """
    model that represents motions in the database
    :param assembly: to which assembly is this motion a part of
    :param motion_text: text box to present motion
    :param date: date when the motion was posted on
    :param arhcived: once a new motion is created, archived = True (representing past motions)
    :param voteable: boolean to allow voting access to students (toggled by a staff member)
    """
    assembly = models.ForeignKey(Assembly, on_delete=models.CASCADE, limit_choices_to={'archived': False})
    motion_text = models.TextField('Content to display', max_length=1000)
    date = models.DateTimeField('date published', default=timezone.now, editable=False)
    archived = models.BooleanField(default=False)
    voteable = models.BooleanField(default=False)
    is_Amendment = models.BooleanField(default=False)

    # choices
    a_favor = models.IntegerField(default=0, editable=False)
    en_contra = models.IntegerField(default=0, editable=False)
    abstenido = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return self.motion_text


class Vote(models.Model):
    """
    model to not allow duplicated votes
    :param student: student that voted on following motion
    :param motion: motion that the student has voted on
    """
    student = models.ForeignKey(base.Student, on_delete=models.CASCADE)
    motion = models.ForeignKey(Motion, on_delete=models.CASCADE)


def create_vote(motion, student):
    """
    helper method to validate if student has not cast a vote already
    :param motion: motion being voted on
    :param student: student voting on the motion
    :return: vote instance if student hasn't voted yet; None if student has voted
    """
    if not vote_exists(motion, student):
        vote = Vote(student=student, motion=motion)
        vote.save()
        return vote
    return None


def vote_exists(motion, student):
    """
    helper method that performs a query search to verify if the student has already successfully voted on the motion
    :param motion: motion being voted on
    :param student: student
    :return:
    """
    try:
        return Vote.objects.get(motion=motion, student=student)
    except:
        return None


class Amendment(Motion):
    """
    model that inhjerits from Motion due to being a special type of motion
    :param motion_amended: relation to which motion it is amending
    """
    motion_amended = models.ForeignKey(Motion, on_delete=models.CASCADE, verbose_name='Motion to be amended',
                                       related_name='original_motion',
                                       limit_choices_to={'archived': False})

    def save(self, *args, **kwargs):
        if not self.is_Amendment:
            self.is_Amendment = True
        super(Amendment, self).save(*args, **kwargs)


def get_prev_model(model):
    """
    helper method that gets the prev model to assign archived = True
    :param model: will receive motion or assembly models
    :return: None if first entry in db; previous entry in db if entries in db is more than 1
    """
    qs = model.objects.order_by('-date')
    if model is Motion:
        qs = model.objects.filter(amendment=None).order_by('-date')
    if len(qs) == 1:
        return None
    else:
        return qs[1]


@receiver(post_save, sender=Motion)
@receiver(post_save, sender=Amendment)
@receiver(post_save, sender=Assembly)
def update_model_archive(sender, instance, created, **kwargs):
    """
    method to assign archive status to previous model
    :param sender: Motion or Assembly model
    :param instance: object entry in database
    :param created: determines if the instance was successfully created
    :param kwargs:
    :return: n/a
    """
    if created:
        model_to_archive = get_prev_model(sender)
        if model_to_archive:
            model_to_archive.archived = True
            model_to_archive.save()
