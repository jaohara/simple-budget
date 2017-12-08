# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-05 01:30
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget_app', '0006_userrecord_def_date_range'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrecord',
            name='max_display_categories',
            field=models.IntegerField(default=8, validators=[django.core.validators.MaxValueValidator(64), django.core.validators.MinValueValidator(2)]),
        ),
    ]
