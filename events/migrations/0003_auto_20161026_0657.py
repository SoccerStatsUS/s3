# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-26 06:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_event_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='object',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='event_against', to='bios.Bio'),
        ),
    ]
