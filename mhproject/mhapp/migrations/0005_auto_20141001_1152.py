# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mhapp', '0004_auto_20140930_1324'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionTrigger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('threshold', models.IntegerField(default=-1, max_length=10)),
                ('description', models.CharField(max_length=500)),
                ('question', models.ForeignKey(to='mhapp.Question')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReportTrigger',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('threshold', models.IntegerField(default=-1, max_length=10)),
                ('type', models.CharField(default='<', choices=[('<', '<'), ('>', '>')], max_length=1)),
                ('description', models.CharField(max_length=500)),
                ('reportType', models.ForeignKey(to='mhapp.ReportType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(default='N', choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('N', 'Not Assigned')], max_length=1),
        ),
    ]
