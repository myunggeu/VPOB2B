# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2019-05-17 23:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0006_auto_20190315_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vpo_desc',
            name='locations',
            field=models.CharField(max_length=60),
        ),
    ]