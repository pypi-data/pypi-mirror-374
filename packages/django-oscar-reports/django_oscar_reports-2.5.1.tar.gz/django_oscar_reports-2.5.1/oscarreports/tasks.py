from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import TYPE_CHECKING, Generic, assert_never
from uuid import UUID
import sys

from django.conf import settings

if TYPE_CHECKING:
    from celery.app.task import Task as _CeleryTask
    from celery.result import AsyncResult as _CeleryAsyncResult
    from django_tasks.task import Task as _DjTask
    from django_tasks.task import TaskResult as _DjTaskResult
else:
    _CeleryTask = Callable
    _CeleryAsyncResult = Generic
    _DjTask = Callable
    _DjTaskResult = Generic


class BackendType(StrEnum):
    CELERY = "celery"
    DJANGO_TASKS = "django-tasks"


class TaskFuture[T]:
    @property
    def id(self) -> str:
        raise NotImplementedError()

    @property
    def status_label(self) -> str | None:
        raise NotImplementedError()


class CeleryTaskFuture[T](TaskFuture[T]):
    _res: _CeleryAsyncResult[T]

    def __init__(self, res: _CeleryAsyncResult[T]) -> None:
        self._res = res

    @property
    def id(self) -> str:
        return str(self._res.id)

    @property
    def status_label(self) -> str | None:
        status = self._res.status
        return str(status).title()


class DjTasksTaskFuture[T](TaskFuture[T]):
    _res: _DjTaskResult[T]

    def __init__(self, res: _DjTaskResult[T]) -> None:
        self._res = res

    @property
    def id(self) -> str:
        return self._res.id

    @property
    def status_label(self) -> str | None:
        status = self._res.status
        # If enum, use name; else cast to string
        return getattr(status, "name", str(status)).title()


class Task[**P, T]:
    backend_type: BackendType

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        raise NotImplementedError()

    def enqueue(self, *args: P.args, **kwargs: P.kwargs) -> TaskFuture[T]:
        raise NotImplementedError()

    def get_result(self, task_id: str) -> TaskFuture[T]:
        raise NotImplementedError()


class CeleryTask[**P, T](Task[P, T]):
    fn: _CeleryTask[P, T]

    def __init__(self, fn: Callable[P, T]) -> None:
        from celery import shared_task

        self.fn = shared_task(ignore_result=True)(fn)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.fn(*args, **kwargs)

    def enqueue(self, *args: P.args, **kwargs: P.kwargs) -> CeleryTaskFuture[T]:
        res = self.fn.apply_async(
            args=args,
            kwargs=kwargs,
            countdown=10,
        )
        return CeleryTaskFuture(res)

    def get_result(self, task_id: str) -> CeleryTaskFuture[T]:
        from celery.result import AsyncResult

        return CeleryTaskFuture[T](AsyncResult(task_id))


class DjTasksTask[**P, T](Task[P, T]):
    fn: _DjTask[P, T]

    def __init__(self, fn: Callable[P, T]) -> None:
        from django_tasks import task

        self.fn = task(enqueue_on_commit=self.enqueue_on_commit)(fn)

    @property
    def enqueue_on_commit(self) -> bool:
        """
        Normally we don't want to send the task until after commit. But, this
        doesn't work with tests since a commit wraps the whole test. So, send
        immediately then.
        """
        is_unit_test = "test" in sys.argv
        return not is_unit_test

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        return self.fn.call(*args, **kwargs)

    def enqueue(self, *args: P.args, **kwargs: P.kwargs) -> DjTasksTaskFuture[T]:
        res = self.fn.enqueue(*args, **kwargs)
        return DjTasksTaskFuture(res)

    def get_result(self, task_id: str) -> DjTasksTaskFuture[T]:
        res = self.fn.get_result(task_id)
        return DjTasksTaskFuture(res)


def task[**P, T](fn: Callable[P, T]) -> Task[P, T]:
    btype_str = getattr(settings, "OSCAR_REPORTS_TASKS_BACKEND", None)
    if btype_str is None:
        try:
            import celery  # NOQA

            btype_str = "celery"
        except ImportError:
            try:
                import django_tasks  # NOQA

                btype_str = "django-tasks"
            except ImportError:
                btype_str = "unknown"

    btype = BackendType(btype_str)
    if btype == BackendType.CELERY:
        return CeleryTask(fn)
    if btype == BackendType.DJANGO_TASKS:
        return DjTasksTask(fn)
    assert_never(btype)


@task
def generate_report(report_uuid: str, report_format: str) -> None:
    from . import models

    report = models.Report.objects.get(uuid=UUID(report_uuid))
    report.generate(report_format)
