# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-18 17:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0003_corpusitemcollection_locked'),
        ('topic_modeling', '0002_auto_20160614_0507'),
    ]

    operations = [
        migrations.CreateModel(
            name='LsiResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_term', models.CharField(max_length=200)),
                ('results', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('collections', models.ManyToManyField(to='core.CorpusItemCollection')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='topicmodelgroup',
            name='options',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
    ]
