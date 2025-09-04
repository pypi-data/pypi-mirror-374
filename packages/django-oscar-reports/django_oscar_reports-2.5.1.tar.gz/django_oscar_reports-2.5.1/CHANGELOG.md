# Changes

## v2.5.1 (2025-09-03)

### Refactor

- migrate black/flake8 -> ruff
- migrate from poetry -> uv

## v2.5.0 (2025-06-12)

### Feat

- support both celery (default) and django-tasks as task queue backends (#29528)
- test against django 5.2

### Fix

- update docker image tag format
- **deps**: update dependency django-oscar to >=4.0,<4.1
- update tests for Oscar 4.0
- **deps**: update dependency celery to >=5.5.1
- **deps**: update dependency django-oscar to >=3.2.6,<4.1
- **deps**: update dependency celery to >=5.5.0

## v2.4.0 (2025-04-03)

### Feat

- add support for Django 5.0

### Fix

- **deps**: update dependency django-stubs-ext to ^5.1.3

### Refactor

- add pyupgrade / django-upgrade precommit hooks

## v2.3.0 (2025-02-06)

### Feat

- add type annotations

## v2.2.3 (2024-09-25)

### Fix

- **deps**: update dependency django-oscar to v3.2.5
- pin django-oscar version due to breaking changes in patch versions

## v2.2.2 (2024-08-31)

## v2.2.2b0 (2024-08-08)

### Fix

- **deps**: update dependency django-oscar to >=3.2.4
- **deps**: update dependency celery to v5.4.0
- **deps**: update dependency django-oscar to v3.2.4
- **deps**: update dependency django to v4.2.13

## v2.2.1 (2023-12-14)

## v2.2.0

- Add support for django-oscar 3.2.2
- Add support for django 4.2

## v2.1.0

- Oscar 3.1 Compatibility

## v2.0.0

- Oscar 3.0 Compatibility

## v1.0.0

- Initial
