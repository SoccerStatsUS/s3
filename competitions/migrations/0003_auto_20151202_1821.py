# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-02 18:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0002_auto_20151202_0655'),
    ]

    operations = [
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('order', models.IntegerField(blank=True, null=True)),
                ('order2', models.IntegerField(blank=True, null=True)),
                ('competition_original_name', models.CharField(max_length=255)),
                ('minutes', models.IntegerField(blank=True, null=True)),
                ('minutes_with_age', models.IntegerField(blank=True, null=True)),
                ('age_minutes', models.FloatField(blank=True, null=True)),
                ('competition', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='competitions.Competition')),
            ],
            options={
                'ordering': ('order', 'super_season__order2', 'competition'),
            },
        ),
        migrations.CreateModel(
            name='SuperSeason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('order', models.IntegerField()),
                ('order2', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='season',
            name='super_season',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='competitions.SuperSeason'),
        ),
    ]
