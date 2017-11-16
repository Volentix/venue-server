# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-16 14:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('venue', '0016_forumprofile_date_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signaturecheck',
            name='uptime_batch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='regular_checks', to='venue.UptimeBatch'),
        ),
    ]
