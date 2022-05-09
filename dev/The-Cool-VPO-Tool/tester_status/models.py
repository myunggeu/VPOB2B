from django.db import models
#from django_mysql.models import JSONField
# Create your models here.

# one entry per site->tester name->cell
class TESTER(models.Model):
    site = models.CharField(max_length=4)
    tester_name = models.PositiveIntegerField()
    cell = models.CharField(max_length=4)
    class Meta:
        unique_together = ('site', 'tester_name', 'cell')

#add one status entry per event.
class STATUS(models.Model):
     tester = models.ForeignKey('Tester', on_delete=models.CASCADE)
     status_up = models.BooleanField()
     details = models.TextField()
     start_time = models.DateTimeField()
     end_time = models.DateTimeField()

# one entry per reservation/person/duration
class RESERVATION(models.Model):
    tester = models.ForeignKey('Tester', on_delete=models.CASCADE)
    user = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

