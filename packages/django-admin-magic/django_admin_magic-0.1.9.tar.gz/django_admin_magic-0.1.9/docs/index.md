# Django Admin Magic

A simple Django app to automatically register your models with the admin site.

- Automatically registers all models from one or more apps
- Sensible defaults for list display, filters, search, and actions
- One-line setup from your admin.py
- Optional auto-discovery across all installed apps
- First-class support for polymorphic models via django-polymorphic
- Utilities like linkify for relations, CSV export, and safe pagination

## Why?
Sometimes you just want to browse your data in Django Admin without writing boilerplate admin classes for every model. Django Admin Magic generates admin classes on the fly with good defaults and lets you customize them incrementally when needed.

## Quick install
```bash
pip install django-admin-magic
```

Enable the app:
```python
INSTALLED_APPS = [
    # ...
    "django_admin_magic",
]
```

Continue with Getting Started to configure and use the library, or jump to the API Reference.
