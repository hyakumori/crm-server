import dateutil
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from django.utils.timezone import now

from hyakumori_crm.archive.service import get_archive_by_pk, get_attachment_by_pk
from hyakumori_crm.archive.utils import decrypt_string, DecryptError


def download_file(request, code):
    try:
        content = decrypt_string(code)
        archive = get_archive_by_pk(content["archive_pk"])
        attachment = get_attachment_by_pk(content["attachment_pk"])
        expired = content["expired"]
        if dateutil.parser.parse(expired) < now():
            return HttpResponseForbidden("expired url")
    except (ObjectDoesNotExist, DecryptError) as e:
        return HttpResponseNotFound()

    response = HttpResponse(attachment.attachment_file, content_type='octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s' % attachment.filename

    return response
