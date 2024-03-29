# Generated by Django 3.0.4 on 2020-07-20 04:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0015_archive_futureaction_text_20200702_1018"),
    ]

    operations = [
        # remove origin customercontact on forestcustomercontact
        # because for now we dont need to create relation forestcustomercontact
        # when add customer for forest, we only do when add contact for forestcustomer
        migrations.RunSQL(
            """delete from crm_forestcustomercontact
where id in (
    select fcc.id from crm_forestcustomercontact fcc
    join crm_forestcustomer fc
    on fc.id = fcc.forestcustomer_id
    join crm_customercontact cc
    on cc.id = fcc.customercontact_id
    join crm_customercontact self_cc
    on self_cc.contact_id = cc.contact_id and self_cc.is_basic = true
    where self_cc.customer_id=fc.customer_id
)"""
        )
    ]
