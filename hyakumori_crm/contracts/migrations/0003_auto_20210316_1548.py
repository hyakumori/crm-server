# Generated by Django 3.1.7 on 2021-03-16 15:48

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0002_auto_20201221_0540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contracttype',
            name='attributes',
            field=models.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
    ]
