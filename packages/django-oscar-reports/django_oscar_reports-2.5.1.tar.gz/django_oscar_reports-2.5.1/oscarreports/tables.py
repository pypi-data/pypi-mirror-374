from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, TemplateColumn
from oscar.apps.dashboard.tables import DashboardTable


class ReportTable(DashboardTable):
    description = Column(accessor="description", orderable=False)
    date_range = TemplateColumn(
        template_name="oscar/dashboard/reports/report_row_date_range.html",
        verbose_name=_("Date Range"),
        orderable=False,
    )

    owner = Column(
        accessor="owner__get_full_name", orderable=False, verbose_name=_("Owner")
    )
    status = Column(
        accessor="status_name", orderable=False, verbose_name=_("Report Status")
    )
    task_status = Column(
        accessor="task_status", orderable=False, verbose_name=_("Task Status")
    )
    filesize = TemplateColumn(
        template_name="oscar/dashboard/reports/report_row_filesize.html",
        verbose_name=_("File Size"),
        orderable=False,
    )

    queued_on = Column(accessor="queued_on")
    started_on = Column(accessor="started_on")
    completed_on = Column(accessor="completed_on")

    actions = TemplateColumn(
        template_name="oscar/dashboard/reports/report_row_actions.html",
        verbose_name=" ",
        orderable=False,
    )

    class Meta(DashboardTable.Meta):
        pass
