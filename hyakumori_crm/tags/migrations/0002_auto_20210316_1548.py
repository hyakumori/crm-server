# Generated by Django 3.1.7 on 2021-03-16 15:48

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tagsetting',
            name='attributes',
            field=models.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
