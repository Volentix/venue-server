# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-24 03:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venue', '0003_userprofile_email_confirmed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumprofile',
            name='verification_code',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]