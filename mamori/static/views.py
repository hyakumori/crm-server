from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
from django.conf import settings

if settings.STATIC_ROOT:
    index_view = never_cache(TemplateView.as_view(template_name="index.html"))
else:
    import requests
    from django.http import StreamingHttpResponse, HttpResponseNotModified

    def index_view(request):
        req_headers = dict(request.headers)
        req_headers.pop("Content-Length")
        req_headers.pop("Content-Type")
        fe_resp = requests.get(
            "http://localhost:8080" + request.get_full_path_info(),
            headers=req_headers,
            stream=True,
        )
        if fe_resp.status_code == 304:
            resp = HttpResponseNotModified()
        else:
            resp = StreamingHttpResponse(
                fe_resp.iter_content(chunk_size=128),
                content_type=fe_resp.headers.get("content-type"),
                status=fe_resp.status_code,
            )
        resp["ETag"] = fe_resp.headers.get("ETag")
        resp["Date"] = fe_resp.headers.get("Date")
        resp["Accept-Ranges"] = fe_resp.headers.get("Accept-Ranges")
        return resp


@never_cache
def test_view(request):
    return HttpResponse("OK", content_type="text/plain")
