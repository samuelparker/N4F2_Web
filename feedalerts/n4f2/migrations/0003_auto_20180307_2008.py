# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-08 04:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('n4f2', '0002_auto_20180219_2142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedprofile',
            name='last_received',
        ),
        migrations.RemoveField(
            model_name='feedprofile',
            name='last_success',
        ),
        migrations.AddField(
            model_name='feedrun',
            name='last_received',
            field=models.DateTimeField(null=True, verbose_name='date received'),
        ),
        migrations.AddField(
            model_name='feedrun',
            name='last_success',
            field=models.DateTimeField(null=True, verbose_name='date published'),
        ),
    ]
