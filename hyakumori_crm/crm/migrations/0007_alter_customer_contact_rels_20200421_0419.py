# Generated by Django 3.0.4 on 2020-04-21 04:19

from django.conf import settings
import django.contrib.postgres.fields.jsonb
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0006_drop_author_editor_20200415_0616'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='archive',
            options={'permissions': [('manage_archive', 'All permissions for archive')]},
        ),
        migrations.AlterModelOptions(
            name='archivecustomer',
            options={},
        ),
        migrations.RemoveField(
            model_name='archivecustomer',
            name='contact',
        ),
        migrations.RemoveField(
            model_name='forestcustomer',
            name='contact',
        ),
        migrations.AlterField(
            model_name='archivecustomer',
            name='archive',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crm.Archive'),
        ),
        migrations.AlterField(
            model_name='archivecustomer',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer'),
        ),
        migrations.AlterField(
            model_name='archiveforest',
            name='archive',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crm.Archive'),
        ),
        migrations.AlterField(
            model_name='archiveforest',
            name='forest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Forest'),
        ),
        migrations.AlterField(
            model_name='customercontact',
            name='contact',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crm.Contact'),
        ),
        migrations.AlterField(
            model_name='customercontact',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer'),
        ),
        migrations.AlterField(
            model_name='forestcustomer',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.Customer'),
        ),
        migrations.AlterField(
            model_name='forestcustomer',
            name='forest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crm.Forest'),
        ),
        migrations.CreateModel(
            name='ForestCustomerContact',
            fields=[
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('attributes', django.contrib.postgres.fields.jsonb.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('customercontact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.CustomerContact')),
                ('forestcustomer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.ForestCustomer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ArchiveUser',
            fields=[
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('attributes', django.contrib.postgres.fields.jsonb.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='crm.Archive')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ArchiveCustomerContact',
            fields=[
                ('deleted', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('attributes', django.contrib.postgres.fields.jsonb.JSONField(default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('archivecustomer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.ArchiveCustomer')),
                ('customercontact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crm.CustomerContact')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
