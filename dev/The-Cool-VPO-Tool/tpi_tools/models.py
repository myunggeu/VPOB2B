from django.db import models

# Create your models here.

class TP(models.Model):
    #the tp name will contain an astrix to replace revision character
    tp_bom = models.CharField(max_length=70, default='empty', primary_key=True)
    vpos = models.TextField()
    mainTP = models.CharField(max_length=30)
    Bom = models.CharField(max_length=10)

class Bin2Bin(models.Model):
    unit = models.CharField(max_length=20, default='empty')
    old_tp_bom = models.CharField(max_length=40, default='empty')
    new_bin = models.CharField(max_length=30, default='empty')
    old_bin = models.CharField(max_length=30, default='empty')
    explanation = models.TextField()
    vmin = models.TextField()
    tester_info = models.TextField()
    tp_name = models.ForeignKey(TP, db_column='tp_bom', null=False, related_name='bin2bin', on_delete=models.CASCADE)
class Meta:
    unique_together = ('tp_name', 'unit')
