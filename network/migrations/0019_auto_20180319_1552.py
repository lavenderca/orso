# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-03-19 19:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0018_auto_20180315_1245'),
    ]

    operations = [
        migrations.CreateModel(
            name='DatasetAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.Dataset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.MyUser')),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_count', models.PositiveIntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.Experiment')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='network.MyUser')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='experimentaccess',
            unique_together=set([('user', 'experiment')]),
        ),
        migrations.AlterUniqueTogether(
            name='datasetaccess',
            unique_together=set([('user', 'dataset')]),
        ),
    ]
