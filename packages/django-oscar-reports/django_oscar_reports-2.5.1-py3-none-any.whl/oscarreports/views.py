from __future__ import annotations

from typing import Any
import os.path

from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseBase,
)
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.detail import BaseDetailView
from django.views.generic.edit import DeleteView, FormMixin
from django_tables2 import SingleTableView

from .forms import ReportForm
from .models import Report
from .tables import ReportTable

try:
    try:
        from psycopg.types.range import Range as DateTimeTZRange
    except ImportError:
        from psycopg2.extras import DateTimeTZRange
except ImportError:
    raise ImproperlyConfigured("Error loading psycopg2 or psycopg module")


class IndexView(FormMixin[ReportForm], SingleTableView):
    template_name = "oscar/dashboard/reports/index.html"
    table_pagination = True  # type:ignore[assignment]
    model = Report
    table_class = ReportTable  # type:ignore[assignment]
    context_table_name = "reports"
    desc_template = ""
    description = ""

    form_class = ReportForm

    def dispatch(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponseBase:
        form_class = self.get_form_class()
        self.form = self.get_form(form_class)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Report]:
        queryset = self.model.objects.all().order_by("-queued_on")
        return queryset

    def get_table_pagination(self, table: ReportTable) -> dict[str, int]:
        return dict(per_page=20)

    def post(
        self,
        request: HttpRequest,
        *args: Any,
        **kwargs: Any,
    ) -> HttpResponse:
        if self.form.is_valid():
            # Create report
            report = Report()
            report.content_type = None
            report.owner = request.user if request.user.is_authenticated else None
            report.type_code = self.form.cleaned_data["report_type"]
            report.date_range = DateTimeTZRange(
                lower=self.form.cleaned_data["date_from"],
                upper=self.form.cleaned_data["date_to"],
            )
            report.save()
            # Queue report
            report.queue()
            # Message user
            messages.info(request, _("Successfully queued report for generation"))
            return redirect("dashboard:reports-index")
        return self.get(request, *args, **kwargs)

    def get_table(self, **kwargs: Any) -> ReportTable:
        table = super().get_table(**kwargs)
        table.caption = _("Reports")
        return table

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        return context


class ReportDownloadView(BaseDetailView[Report]):
    model = Report
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def render_to_response(
        self,
        context: dict[str, Any],
        **response_kwargs: Any,
    ) -> FileResponse:
        report = context["object"]
        if not report.report_file.name:
            raise Http404()
        # Build filename
        extension = os.path.splitext(report.report_file.name)[1].replace(".", "")
        filename = "{date}_{type_code}_{uuid}.{ext}".format(
            date=report.created_on.strftime("%Y-%m-%d"),
            type_code=report.type_code,
            uuid=report.uuid,
            ext=extension,
        )
        # Send file to client
        resp = FileResponse(report.report_file, as_attachment=True, filename=filename)
        resp["Content-Type"] = report.mime_type
        return resp


class ReportDeleteView(DeleteView[Report, BaseModelForm[Report]]):
    model = Report
    slug_field = "uuid"
    slug_url_kwarg = "uuid"
    success_url = reverse_lazy("dashboard:reports-index")
    template_name = "oscar/dashboard/reports/report_confirm_delete.html"
