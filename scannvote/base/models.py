from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Student(models.Model):
    # TODO consultar con el cge para las opciones (if any)
    faculty_choices = {
        ('ingenieria', 'ingeniería'),
        ('biologia', 'biología'),
        ('humanidades', 'humanidades'),
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=9, blank=False, unique=True,)
    faculty = models.CharField(max_length=50, choices=faculty_choices)

    def __str__(self):
        return self.student_id

    def student_exists(self, sid):
        return Student.objects.filter(student_id=sid)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(user=instance)
    instance.student.save()
