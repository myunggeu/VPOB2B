# Generated by Django 3.1.2 on 2022-03-08 18:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0007_auto_20190517_1659'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test_time_module',
            name='instance_and_tt',
        ),
        migrations.RemoveField(
            model_name='test_time_tp',
            name='module_and_tt',
        ),
    ]
