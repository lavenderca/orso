# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-17 19:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0015_datarecommendation_reference_dataset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='owners',
            field=models.ManyToManyField(blank=True, to='network.MyUser'),
        ),
    ]