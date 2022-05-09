# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-16 21:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RESERVATION',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='STATUS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_up', models.BooleanField()),
                ('details', models.TextField()),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='TESTER',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site', models.CharField(max_length=4)),
                ('tester_name', models.PositiveIntegerField()),
                ('cell', models.CharField(max_length=4)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='tester',
            unique_together=set([('site', 'tester_name', 'cell')]),
        ),
        migrations.AddField(
            model_name='status',
            name='tester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tester_status.TESTER'),
        ),
        migrations.AddField(
            model_name='reservation',
            name='tester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tester_status.TESTER'),
        ),
    ]
