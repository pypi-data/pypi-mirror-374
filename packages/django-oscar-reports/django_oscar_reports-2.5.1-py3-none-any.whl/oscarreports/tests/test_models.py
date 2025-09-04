from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from .. import models

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
        self.staff_user = User.objects.create_user(
            username="root", email="root@example.com", is_staff=True
        )

        self.report = models.Report()
        self.report.uuid = "d3c74a8b-e7ae-4482-bd9c-bee69fde5c5c"
        self.report.content_type = None
        self.report.owner = self.staff_user
        self.report.type_code = "order_report"
        self.report.date_range = DateTimeTZRange(
            lower=(timezone.now() - timedelta(days=1)), upper=(timezone.now())
        )
        self.report.save()

    def test_str(self) -> None:
        self.assertEqual(str(self.report), "d3c74a8b-e7ae-4482-bd9c-bee69fde5c5c")

    def test_status(self) -> None:
        self.report.queued_on = None
        self.report.started_on = None
        self.report.completed_on = None
        self.report.save()
        self.assertEqual(self.report.status, "created")
        self.assertEqual(self.report.status_name, "Created")
        self.assertFalse(self.report.is_complete)

        self.report.queued_on = timezone.now()
        self.report.save()
        self.assertEqual(self.report.status, "queued")
        self.assertEqual(self.report.status_name, "Queued")
        self.assertFalse(self.report.is_complete)

        self.report.started_on = timezone.now()
        self.report.save()
        self.assertEqual(self.report.status, "in-progress")
        self.assertEqual(self.report.status_name, "In-Progress")
        self.assertFalse(self.report.is_complete)

        self.report.completed_on = timezone.now()
        self.report.save()
        self.assertEqual(self.report.status, "completed")
        self.assertEqual(self.report.status_name, "Completed")
        self.assertTrue(self.report.is_complete)

    def test_generator_class(self) -> None:
        self.assertEqual(self.report.generator_class.description, "Orders placed")

    def test_generator_class_missing(self) -> None:
        self.report.type_code = "foo_bar_baz"
        with self.assertRaises(ValueError):
            print(self.report.generator_class)

    @mock.patch("oscarreports.tasks.generate_report")
    def test_queue(self, mock_generate_report: mock.MagicMock) -> None:
        task = mock.MagicMock()
        task.id = "f3a0b0a0-148a-4ba1-9ed4-dd5543e77d73"
        mock_generate_report.enqueue.return_value = task

        self.assertEqual(mock_generate_report.enqueue.call_count, 0)

        self.assertEqual(self.report.description, "")
        self.assertIsNone(self.report.queued_on)
        self.assertIsNone(self.report.started_on)
        self.assertIsNone(self.report.completed_on)
        self.assertIsNone(self.report.task_id)

        self.report.queue()

        self.assertEqual(mock_generate_report.enqueue.call_count, 1)
        mock_generate_report.enqueue.assert_called_once_with(
            "d3c74a8b-e7ae-4482-bd9c-bee69fde5c5c",
            "CSV",
        )

        self.assertTrue(self.report.description.startswith("Orders placed between"))
        self.assertIsNotNone(self.report.queued_on)
        self.assertIsNone(self.report.started_on)
        self.assertIsNone(self.report.completed_on)
        self.assertEqual(self.report.task_id, "f3a0b0a0-148a-4ba1-9ed4-dd5543e77d73")

    def test_generate(self) -> None:
        self.assertIsNone(self.report.started_on)
        self.assertIsNone(self.report.mime_type)
        self.assertIsNone(self.report.report_file.name)
        self.assertIsNone(self.report.completed_on)

        self.report.generate()

        self.assertIsNotNone(self.report.started_on)
        self.assertEqual(self.report.mime_type, "text/csv")
        self.assertTrue(
            self.report.report_file.name.startswith(
                "oscar-reports/2019/10/03/d3c74a8b-e7ae-4482-bd9c-bee69fde5c5c"
            )
        )
        self.assertTrue(self.report.report_file.name.endswith(".csv"))
        self.assertIsNotNone(self.report.completed_on)

    def test_queue_integration(self) -> None:
        self.assertEqual(self.report.description, "")
        self.assertIsNone(self.report.queued_on)
        self.assertIsNone(self.report.started_on)
        self.assertIsNone(self.report.completed_on)
        self.assertIsNone(self.report.task_id)
        self.assertIsNone(self.report.mime_type)
        self.assertIsNone(self.report.report_file.name)
        self.assertEqual(len(mail.outbox), 0)

        task = self.report.queue()

        self.report.refresh_from_db()

        self.assertTrue(self.report.description.startswith("Orders placed between"))
        self.assertIsNotNone(self.report.queued_on)
        self.assertIsNotNone(self.report.started_on)
        self.assertIsNotNone(self.report.completed_on)
        self.assertEqual(str(self.report.task_id), task.id)
        self.assertEqual(self.report.mime_type, "text/csv")
        self.assertTrue(
            self.report.report_file.name.startswith(
                "oscar-reports/2019/10/03/d3c74a8b-e7ae-4482-bd9c-bee69fde5c5c"
            )
        )
        self.assertTrue(self.report.report_file.name.endswith(".csv"))

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            "Your report is ready to download | Orders placed between Oct. 2, 2019 and Oct. 3, 2019",
        )

    def test_delete(self) -> None:
        self.report.generate()
        self.report.report_file.delete = mock.MagicMock()

        self.assertEqual(self.report.report_file.delete.call_count, 0)

        self.report.delete()

        self.assertEqual(self.report.report_file.delete.call_count, 1)
        self.report.report_file.delete.assert_called_once_with(save=False)
