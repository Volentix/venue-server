# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-08-18 15:09
from __future__ import unicode_literals

from django.db import migrations, models


def migrate_language_codes(apps, schema_editor):
    UserProfile = apps.get_model('venue', 'UserProfile')
    for u in UserProfile.objects.all().prefetch_related('language'):
        u.language_code = u.language.code
        u.save()


class Migration(migrations.Migration):

    dependencies = [
        ('venue', '0010_leader_board_stored_procedure_fix'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='language_code',
            field=models.CharField(choices=[('en', 'English'), ('tr', 'Turkish')], default='en', max_length=5),
        ),
        migrations.RunPython(migrate_language_codes),
    ]
