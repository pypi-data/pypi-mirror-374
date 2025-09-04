from django.contrib import admin

from . import models


@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin[models.Report]):
    search_fields = ["uuid"]
    raw_id_fields = ["owner"]
    list_display = [
        "uuid",
        "owner",
        "content_type",
        "type_code",
        "created_on",
        "queued_on",
        "started_on",
        "completed_on",
        "status_name",
    ]
    list_filter = [
        "type_code",
        "created_on",
        "queued_on",
        "started_on",
        "completed_on",
    ]
    readonly_fields = [
        "uuid",
        "task_id",
        "created_on",
    ]
    fields = [
        "uuid",
        "content_type",
        "type_code",
        "owner",
        "description",
        "date_range",
        "task_id",
        "created_on",
        "queued_on",
        "started_on",
        "completed_on",
        "mime_type",
        "report_file",
    ]
