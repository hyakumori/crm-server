from hyakumori_crm.crm.models.customer import Contact

from data_import.lib.common import BaseMigration


class Migration(BaseMigration):
    def migrate(self):
        contacts = Contact.objects.all()
        total = contacts.count()
        current = 0

        for contact in contacts.iterator():
            current += 1
            print(f"migrating ... {current}/{total}")
            contact.name_kanji = contact.contact_info["name_kanji"]
            contact.name_kana = contact.contact_info["name_kana"]
            contact.address = contact.customercontact_set.first().customer.address
            contact.postal_code = contact.contact_info["postal_code"]
            contact.telephone = contact.contact_info["telephone"]
            contact.mobilephone = contact.contact_info["mobilephone"]
            contact.email = contact.contact_info["email"]
            contact.save()
