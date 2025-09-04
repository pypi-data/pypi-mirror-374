from __future__ import annotations

import io
import os.path
import uuid

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import StrOrPromise
from oscar.apps.dashboard.reports.reports import ReportGenerator
from oscar.models.fields import NullCharField

from . import tasks
from .utils import GeneratorRepository


def get_report_upload_path(instance: Report, filename: str) -> str:
    # Upload files to {MEDIA_ROOT}/{OSCAR_REPORTS_UPLOAD_PREFIX}/{YYYY}/{MM}/{DD}/{uuid}.{ext}
    prefix = getattr(settings, "OSCAR_REPORTS_UPLOAD_PREFIX", "oscar-reports")
    extension = os.path.splitext(filename)[1].replace(".", "")
    return "{prefix}/{date}/{uuid}.{ext}".format(
        prefix=prefix,
        date=instance.created_on.strftime("%Y/%m/%d"),
        uuid=instance.uuid,
        ext=extension,
    )


class Report(models.Model):
    STATUS_CREATED = "created"
    STATUS_QUEUED = "queued"
    STATUS_IN_PROGRESS = "in-progress"
    STATUS_COMPLETED = "completed"
    STATUS_NAMES = {
        STATUS_CREATED: _("Created"),
        STATUS_QUEUED: _("Queued"),
        STATUS_IN_PROGRESS: _("In-Progress"),
        STATUS_COMPLETED: _("Completed"),
    }

    # Unique ID used in URLs and filenames
    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False, unique=True)

    # Store a link to the content-type (model) which was used to generate this report.
    # Only user's with the `can_view` permission on this content-type will be able to
    # see this report.
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_("Content Type"),
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
        blank=True,
    )

    # Report Metadata
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Owner"),
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    type_code = models.CharField(_("Type Code"), max_length=50)
    description = models.TextField(_("Description"))
    date_range = DateTimeRangeField(  # type:ignore[misc]
        _("Date Range"),
        null=True,
        blank=True,
    )

    # Background Task ID (UUID for Celery, opaque string for django-tasks)
    task_id = models.CharField(
        _("Background Task ID"),
        editable=False,
        unique=True,
        null=True,
        blank=True,
        max_length=64,
    )

    # Status Timestamps
    created_on = models.DateTimeField(_("Created On"), auto_now_add=True)
    queued_on = models.DateTimeField(_("Queued On"), null=True, blank=True)
    started_on = models.DateTimeField(_("Started On"), null=True, blank=True)
    completed_on = models.DateTimeField(_("Completed On"), null=True, blank=True)

    # Report File Output
    mime_type = NullCharField(_("MIME Type"), max_length=20)
    report_file = models.FileField(
        _("Report File"), upload_to=get_report_upload_path, null=True, blank=True
    )

    def __str__(self) -> str:
        return str(self.uuid)

    @property
    def status(self) -> str:
        if self.completed_on:
            return self.STATUS_COMPLETED
        if self.started_on:
            return self.STATUS_IN_PROGRESS
        if self.queued_on:
            return self.STATUS_QUEUED
        return self.STATUS_CREATED

    @property
    def status_name(self) -> StrOrPromise:
        return self.STATUS_NAMES.get(self.status, "")

    @property
    def is_complete(self) -> bool:
        return self.status == self.STATUS_COMPLETED

    @property
    def generator_class(
        self,
    ) -> type[ReportGenerator]:
        generator = GeneratorRepository().get_generator(self.type_code)
        if not generator:
            raise ValueError("Can not queue report: no generator class was found.")
        return generator

    @property
    def task_result(self) -> tasks.TaskFuture[None] | None:
        if not self.task_id:
            return None
        return tasks.generate_report.get_result(self.task_id)

    @property
    def task_status(self) -> str | None:
        result_future = self.task_result
        if result_future is None:
            return None
        return result_future.status_label

    def queue(
        self,
        report_format: str = "CSV",
    ) -> tasks.TaskFuture[None]:
        # Reset metadata
        generator = self.get_generator(report_format)
        self.description = generator.report_description()
        self.queued_on = None
        self.started_on = None
        self.completed_on = None
        self.task_id = None
        self.save(
            update_fields=[
                "description",
                "queued_on",
                "started_on",
                "completed_on",
                "task_id",
            ]
        )
        # Schedule the report generation job
        task = tasks.generate_report.enqueue(str(self.uuid), report_format)
        # Update the task metadata
        self.queued_on = timezone.now()
        self.task_id = task.id
        self.save(
            update_fields=[
                "queued_on",
                "task_id",
            ]
        )
        return task

    queue.alters_data = True  # type:ignore[attr-defined]

    def generate(self, report_format: str = "CSV") -> None:
        # Record start time
        self.started_on = timezone.now()
        self.save(update_fields=["started_on"])
        # Generate report content
        generator = self.get_generator(report_format)
        report = generator.generate()
        # Save generated content
        filename = self.get_filename(report_format)
        content = io.BytesIO(report.content)
        self.mime_type = report["content-type"]
        self.report_file.save(filename, content)
        self.completed_on = timezone.now()
        self.save(
            update_fields=[
                "mime_type",
                "report_file",
                "completed_on",
            ]
        )
        self.send_completed_alert()

    generate.alters_data = True  # type:ignore[attr-defined]

    def send_completed_alert(self) -> None:
        if self.owner is None or not self.owner.email:
            return
        ctx = {
            "site": Site.objects.get_current(),
            "report": self,
        }
        subject = get_template(
            "oscar/dashboard/reports/emails/report_completed_alert_subject.txt"
        ).render(ctx)
        subject = subject.replace("\n", "")
        text = get_template(
            "oscar/dashboard/reports/emails/report_completed_alert_body.txt"
        ).render(ctx)
        html = get_template(
            "oscar/dashboard/reports/emails/report_completed_alert_body.html"
        ).render(ctx)
        to_addrs = [self.owner.email]
        msg = EmailMultiAlternatives(subject, text, settings.OSCAR_FROM_EMAIL, to_addrs)
        msg.attach_alternative(html, "text/html")
        msg.send()

    send_completed_alert.alters_data = True  # type:ignore[attr-defined]

    def get_generator(
        self,
        report_format: str,
    ) -> ReportGenerator:
        kwargs = {
            "start_date": self.date_range.lower if self.date_range else None,
            "end_date": self.date_range.upper if self.date_range else None,
            "formatter": report_format,
        }
        return self.generator_class(**kwargs)

    def get_filename(self, report_format: str) -> str:
        return f"{self.uuid}.{report_format.lower()}"
