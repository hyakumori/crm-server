# Generated by Django 3.1.7 on 2021-03-16 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionlog',
            name='changes',
            field=models.JSONField(blank=True, verbose_name='change diff'),
        ),
        migrations.AlterField(
            model_name='actionlog',
            name='template_data',
            field=models.JSONField(blank=True, null=True, verbose_name='template rendering data'),
        ),
    ]
