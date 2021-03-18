import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# CGE focused models


class Assembly(models.Model):
    assembly_name = models.CharField(max_length=200, default="")
    date = models.DateTimeField('event date')
    quorum = models.IntegerField(default=0, editable=False)
    agenda = models.CharField(max_length=500, default="Placeholder")

    def __str__(self):
        return self.assembly_name

    class Meta:
        verbose_name_plural = "Assemblies"


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

# User focused models


class Student(models.Model):
    faculty_choices = {
        ('ingenieria', 'ingeniería'),
        ('biologia', 'biología'),
        ('humanidades', 'humanidades'),
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.IntegerField(default=0)
    faculty = models.CharField(max_length=50, choices=faculty_choices)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.student.save()

