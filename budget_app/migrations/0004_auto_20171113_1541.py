# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-13 23:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget_app', '0003_auto_20171106_2111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrecord',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
