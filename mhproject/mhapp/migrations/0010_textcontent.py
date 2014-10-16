# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhapp', '0009_auto_20141009_0559'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('text', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
