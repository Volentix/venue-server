# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-18 01:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venue', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataupdatetask',
            name='task_id',
            field=models.CharField(max_length=50),
        ),
    ]
