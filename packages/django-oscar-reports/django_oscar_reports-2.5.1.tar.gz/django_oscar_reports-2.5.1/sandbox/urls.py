from django.apps import apps
from django.conf import settings
from django.conf.urls import i18n as i18n_urls
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve

oscar = apps.get_app_config("oscar")

urlpatterns = [
    path("i18n/", include(i18n_urls)),
    path("admin/", admin.site.urls),
    path(
        "media/<path:path>",
        serve,
        {"document_root": settings.MEDIA_ROOT, "show_indexes": True},
    ),
    # Include Oscar
    path("", include(oscar.urls[0])),  # type:ignore[attr-defined]
]
