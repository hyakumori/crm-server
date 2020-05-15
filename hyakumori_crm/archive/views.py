import dateutil
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from django.utils.translation import gettext as _

from hyakumori_crm.archive.service import get_attachment_by_pk
from hyakumori_crm.crm.common.utils import DecryptError, decrypt_string


def download_file(request, code):
    try:
        content = decrypt_string(code)
        attachment = get_attachment_by_pk(content["attachment_pk"])
        expired = content["expired"]
        if dateutil.parser.parse(expired) < now():
            return JsonResponse(data={"message": _("expired url")}, status=410)

        response = HttpResponse(attachment.attachment_file, content_type="octet-stream")
        response["Content-Disposition"] = (
            "attachment; filename=%s" % attachment.filename
        )

        return response
    except (ObjectDoesNotExist, DecryptError, FileNotFoundError) as e:
        return JsonResponse(data={"message": _("file not found")}, status=404)
