# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhapp', '0008_auto_20141009_1123'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='address',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='interests',
        ),
        migrations.AddField(
            model_name='profile',
            name='concern',
            field=models.ForeignKey(blank=True, to='mhapp.Concern', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='notify',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
