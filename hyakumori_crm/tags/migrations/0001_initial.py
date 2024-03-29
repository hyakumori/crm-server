# Generated by Django 3.0.4 on 2020-05-04 04:41

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TagSetting',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('attributes', django.contrib.postgres.fields.jsonb.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('name', models.CharField(max_length=255, verbose_name='tag name')),
                ('code', models.CharField(max_length=255, verbose_name='slug alike sanitized')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.ContentType', verbose_name='content type')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='authored_tagsetting', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'tag setting',
                'verbose_name_plural': 'tag settings',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='tagsetting',
            constraint=models.UniqueConstraint(fields=('name', 'code', 'content_type'), name='unique_tag_setting'),
        ),
    ]
