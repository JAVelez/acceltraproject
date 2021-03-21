from django.db import models
from django.utils import timezone

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
