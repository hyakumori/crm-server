from django.urls import path

from .restful import reload_single_archive_cache, reload_forest_cache

api_urls = [
    path(
        "cache/archives/<uuid:pk>",
        view=reload_single_archive_cache,
        name="reload-single-archive-cache",
    ),
    path("cache/forests", view=reload_forest_cache, name="reload-forest-cache",),
]
