# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-02 10:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('arm_wells', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='well_summary',
            field=models.TextField(blank=True, default=b''),
        ),
    ]
