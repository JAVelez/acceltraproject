from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Student(models.Model):
    """
    model to add student values not found in Django's user model
    :param: user: one to one relation to Django's user model to use their authentication with added values
    :param: student_id: student id number
    :param: faculty: faculty to which the student belongs to
    :param: attending: will alternate from False and True depending if the student is attending an assembly
    """
    # TODO consultar con el cge para las opciones (if any)
    faculty_choices = {
        ('none', 'none'),
        ('ingenieria', 'ingeniería'),
        ('biologia', 'biología'),
        ('humanidades', 'humanidades'),
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=9, blank=False, unique=True,)
    faculty = models.CharField(max_length=50, choices=faculty_choices, default='none')
    attending = models.BooleanField(default=False)

    def __str__(self):
        return self.student_id

    @staticmethod
    def student_exists(sid):
        return Student.objects.filter(student_id=sid)

    @staticmethod
    def get_student_by_user(user):
        return Student.objects.get(user=user)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    """
    method that is called when Django sends the signal a User is created to also create the student and relate it to
    the user just created
    :param sender: model who sends the signal
    :param instance: object that has sent the signal
    :param created: determines if the User was created successfully
    :param kwargs:
    :return:
    """
    if created:
        Student.objects.create(user=instance)
    instance.student.save()
