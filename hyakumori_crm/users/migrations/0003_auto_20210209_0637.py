# Generated by Django 3.1.6 on 2021-02-09 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_added_username_20200412_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]