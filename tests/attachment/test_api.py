import pytest
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory, force_authenticate

from hyakumori_crm.archive.restful import archives
from hyakumori_crm.crm.models.archive import Archive


@pytest.mark.django_db
def set_up(admin_user):
    # archive = Archive(id="54489ef2-40d9-406e-9996-48cdeba1f4c5", title="Sunflower", content="Hello World",
    #                   location="Da Nang", archive_date="2020-02-11")
    # archive.save()
    archive2 = Archive(id="8e1a4f73-00b0-4f5e-b5fa-7af23ff6b117 ", title="Sunflower2", content="Hello World2",
                       location="Da Nang2", archive_date="2020-02-11")
    archive2.save()
    factory = APIRequestFactory()
    with open(f'{os.getcwd()}/tests/attachment/file1.txt', 'r') as file:
        upload_file = SimpleUploadedFile('hello', file.read(), content_type='multipart/form-data')
        req = factory.post('/archives/8e1a4f73-00b0-4f5e-b5fa-7af23ff6b117/attachments', {
            'file': upload_file
        })
        force_authenticate(req, user=admin_user)
        res = archives(req)
        print(res.status_code)
        assert res.status_code == 200
