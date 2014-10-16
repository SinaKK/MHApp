# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhapp', '0002_concern'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='date_created',
            field=models.DateField(auto_now_add=True),
        ),
    ]
