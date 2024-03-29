# Generated by Django 3.0.4 on 2020-05-22 04:14

import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContractType',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('attributes', django.contrib.postgres.fields.jsonb.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='contract type name')),
                ('code', models.CharField(max_length=255, unique=True, verbose_name='contract code name, reversed enum value')),
                ('description', models.TextField(blank=True, null=True, verbose_name='contract type description')),
            ],
            options={
                'verbose_name': 'contract type',
                'verbose_name_plural': 'contract type',
                'ordering': ['-created_at'],
            },
        ),
    ]
