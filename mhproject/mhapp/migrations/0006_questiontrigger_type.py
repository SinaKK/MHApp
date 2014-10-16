# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhapp', '0005_auto_20141001_1152'),
    ]

    operations = [
        migrations.AddField(
            model_name='questiontrigger',
            name='type',
            field=models.CharField(choices=[('<', '<'), ('>', '>')], default='<', max_length=1),
            preserve_default=True,
        ),
    ]
