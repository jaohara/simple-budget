# Generated by Django 2.0 on 2017-12-19 04:40

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget_app', '0009_auto_20171206_0812'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrecord',
            name='current_funds',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=64),
        ),
    ]
