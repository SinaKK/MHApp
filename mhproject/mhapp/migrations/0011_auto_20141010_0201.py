# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhapp', '0010_textcontent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questiontrigger',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='reporttrigger',
            name='description',
            field=models.TextField(),
        ),
    ]
