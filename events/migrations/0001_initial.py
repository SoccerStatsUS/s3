# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-26 02:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bios', '0002_auto_20151202_1842'),
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minute', models.IntegerField(null=True)),
                ('etype', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=255)),
                ('game', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='games.Game')),
                ('object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_against', to='bios.Bio')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='event_committed', to='bios.Bio')),
            ],
        ),
    ]
