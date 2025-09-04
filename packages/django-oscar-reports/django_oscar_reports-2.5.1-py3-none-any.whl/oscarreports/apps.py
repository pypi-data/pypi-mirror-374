from django.urls import path
from django.urls.resolvers import URLPattern
from oscar.apps.dashboard.reports import apps


class ReportsDashboardConfig(apps.ReportsDashboardConfig):
    name = "oscarreports"

    def ready(self) -> None:
        super().ready()
        from . import handlers, views  # NOQA

        self.index_view = views.IndexView
        self.download_view = views.ReportDownloadView
        self.delete_view = views.ReportDeleteView

    def get_urls(self) -> list[URLPattern]:
        urls = [
            path("", self.index_view.as_view(), name="reports-index"),
            path(
                "<uuid:uuid>/download/",
                self.download_view.as_view(),
                name="reports-download",
            ),
            path(
                "<uuid:uuid>/delete/",
                self.delete_view.as_view(),
                name="reports-delete",
            ),
        ]
        return self.post_process_urls(urls)
