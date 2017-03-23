from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


# Create your models here.
class University(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('University')
        verbose_name_plural = _('Universities')

    def __str__(self):
        return self.name


class Student(models.Model):
    university = models.ForeignKey(University)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')

    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)
