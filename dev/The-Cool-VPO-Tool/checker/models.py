from django.db import models
#from django_mysql.models import JSONField
# Create your models here.


class VPO_DESC(models.Model):
    tp = models.CharField(max_length=30)
    bom = models.CharField(max_length=15)
    ww = models.CharField(max_length=10, default="")
    vpo = models.CharField(max_length=13, default="")
    site = models.CharField(max_length=6)
    units = models.IntegerField()
    device = models.CharField(max_length=20)
    source_lot = models.CharField(max_length=100)
    locations = models.CharField(max_length=60)
    description = models.TextField()


class VPO_LOC(models.Model):
    vpo = models.CharField(max_length=13, default="")
    location = models.IntegerField(default=0)
    status = models.BooleanField(default=False)
    bin_desc = models.CharField(max_length=300, default="")
    yield_val = models.CharField(max_length=20, default="")
    vpo_program = models.TextField(default="")
    vpo_part = models.TextField(default="")
    class Meta:
        unique_together = ('vpo', 'location')


class Plan(models.Model):
    tp = models.CharField(max_length=30)
    ww = models.IntegerField()


class PLAN_STATUS(models.Model):
    ptp = models.CharField(max_length=30)
    pbom = models.CharField(max_length=15)
    ppilots = models.BooleanField(default=False)
    pyield = models.BooleanField(default=False)
    pbs = models.BooleanField(default=False)
    ptherm = models.BooleanField(default=False)
    pb2b = models.BooleanField(default=False)
    pqa = models.BooleanField(default=False)
    pinitwtl = models.BooleanField(default=False)
    pfinwtl = models.BooleanField(default=False)
    pfwp = models.BooleanField(default=False)
    pfuse = models.BooleanField(default=False)




class TEST_TIME_TP(models.Model):
    product = models.CharField(max_length=3)
    bom = models.CharField(max_length=15, blank=False)
    location = models.CharField(max_length=6,blank=False)
    tp = models.CharField(max_length=20, blank=False)
    phi = models.IntegerField(default=0)
    #module_and_tt = JSONField()


class TEST_TIME_MODULE(models.Model):
    product = models.CharField(max_length=3)
    bom = models.CharField(max_length=15, blank=False)
    location = models.CharField(max_length=6, blank=False)
    tp = models.CharField(max_length=20, blank=False)
    team = models.CharField(max_length = 20)
    module = models.CharField(max_length=20)
    #instance_and_tt = JSONField()