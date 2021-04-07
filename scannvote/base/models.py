from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import When


class Student(models.Model):
    faculty_choices = {
        ('ingenieria', 'ingeniería'),
        ('biologia', 'biología'),
        ('humanidades', 'humanidades'),
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=9, blank=False, unique=True,
                                  error_messages={'unique': ("A user with that username already exists."), }, )
    faculty = models.CharField(max_length=50, choices=faculty_choices)
    choices = {('true', 'presente'),
               ('false', 'no presente')}
    is_present = models.CharField(max_length=20, choices=choices)#, default='false')

    def __str__(self):
        return self.student_id

    def student_exists(self, sid):
        return Student.objects.filter(student_id=sid)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(user=instance)
    instance.student.save()


class Quorum(models.Model):
    users = models.ForeignKey(Student, on_delete=models.CASCADE)
    isPresent = models.CharField(max_length=100, default="true")
     #if Student.is_present == 'true':
     #   users = models.ForeignKey(Student, on_delete=models.CASCADE, default="")
     #   isPresent = models.CharField(max_length=100, default="true")
