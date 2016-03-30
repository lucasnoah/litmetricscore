# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-11 20:12
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='TopicModelGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_data', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TopicTuple',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.FloatField()),
                ('word', models.CharField(max_length=150)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topic_modeling.Topic')),
            ],
        ),
        migrations.AddField(
            model_name='topic',
            name='topic_model_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topic_modeling.TopicModelGroup'),
        ),
    ]
