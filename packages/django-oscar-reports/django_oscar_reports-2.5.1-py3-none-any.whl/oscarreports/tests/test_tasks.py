from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from .. import models, tasks

try:
    try:
        from psycopg.types.range import Range as DateTimeTZRange
    except ImportError:
        from psycopg2.extras import DateTimeTZRange
except ImportError:
    raise ImproperlyConfigured("Error loading psycopg2 or psycopg module")


@freeze_time("2019-10-03T12:00:00-04:00")
class ReportTest(TestCase):
    def setUp(self) -> None:
        self.staff_user = User.objects.create_user(username="root", is_staff=True)

        self.report = models.Report()
        self.report.uuid = "d3c74a8b-e7ae-4482-bd9c-bee69fde5c5c"
        self.report.content_type = None
        self.report.owner = self.staff_user
        self.report.type_code = "order_report"
        self.report.date_range = DateTimeTZRange(
            lower=(timezone.now() - timedelta(days=1)), upper=(timezone.now())
        )
        self.report.save()

    def test_generate_report(self) -> None:
        self.assertIsNone(self.report.started_on)
        self.assertIsNone(self.report.mime_type)
        self.assertIsNone(self.report.report_file.name)
        self.assertIsNone(self.report.completed_on)

        tasks.generate_report.enqueue(str(self.report.uuid), "CSV")

        self.report.refresh_from_db()

        self.assertIsNotNone(self.report.started_on)
        self.assertEqual(self.report.mime_type, "text/csv")
        self.assertTrue(
            self.report.report_file.name.startswith(
                "oscar-reports/2019/10/03/d3c74a8b-e7ae-4482-bd9c-bee69fde5c5c"
            )
        )
        self.assertTrue(self.report.report_file.name.endswith(".csv"))
        self.assertIsNotNone(self.report.completed_on)
