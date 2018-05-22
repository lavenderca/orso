# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-05-22 15:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0032_auto_20180522_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='dendrogram',
            name='my_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='network.MyUser'),
        ),
        migrations.AlterUniqueTogether(
            name='dendrogram',
            unique_together=set([('organism', 'experiment_type', 'my_user')]),
        ),
    ]
