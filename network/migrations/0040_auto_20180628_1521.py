# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-06-28 19:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0039_auto_20180627_1746'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='filtered_intersection_values',
        ),
        migrations.AddField(
            model_name='dataset',
            name='predicted_cell_type',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='dataset',
            name='predicted_target',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
