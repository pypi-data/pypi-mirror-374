# Django Commands Suite

**Django Commands Suite** is a Django app that provides a **powerful set of management commands** ready to use in your Django projects.

This package helps you automate repetitive tasks like database backup, seeding, cache management, and logging command executions.

---

## **Installation**

Install the package via pip:

```bash
pip install django-commands-suite
```

---

## **Usage**

1. Add `django_commands_suite` to your `INSTALLED_APPS` in `settings.py`:

    ```python
    INSTALLED_APPS = [
        ...
        'django_commands_suite',
    ]
    ```

2. Run migrations to create database tables

    ```bash
    python manage.py makemigrations django_commands_suite
    python manage.py migrate
    ```