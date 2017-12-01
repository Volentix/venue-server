# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-12-01 03:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venue', '0005_signaturecheck_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalstats',
            name='total_days',
            field=models.DecimalField(decimal_places=4, max_digits=12),
        ),
        migrations.AlterField(
            model_name='pointscalculation',
            name='influence_points',
            field=models.DecimalField(decimal_places=4, max_digits=12),
        ),
        migrations.AlterField(
            model_name='pointscalculation',
            name='post_days_points',
            field=models.DecimalField(decimal_places=4, max_digits=12),
        ),
        migrations.AlterField(
            model_name='pointscalculation',
            name='post_points',
            field=models.DecimalField(decimal_places=4, max_digits=12),
        ),
        migrations.AlterField(
            model_name='pointscalculation',
            name='total_points',
            field=models.DecimalField(decimal_places=4, max_digits=12),
        ),
    ]
