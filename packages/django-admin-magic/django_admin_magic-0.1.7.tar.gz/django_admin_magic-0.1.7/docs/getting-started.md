# Getting Started

## Installation
```bash
pip install django-admin-magic
```

Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ...
    "django_admin_magic",
]
```

## Quickstart
Register all models for a specific app from its `admin.py`:
```python
from django_admin_magic.utils import create_auto_admin_registrar

registrar = create_auto_admin_registrar()  # infers current app label
# or explicitly
# registrar = create_auto_admin_registrar("my_app")
```

Register multiple apps:
```python
from django_admin_magic.utils import create_auto_admin_registrar_for_apps

registrar = create_auto_admin_registrar_for_apps(["app1", "app2"]) 
```

Register all discovered apps that have models:
```python
from django_admin_magic.utils import create_auto_admin_registrar_for_all_apps

registrar = create_auto_admin_registrar_for_all_apps()
```

## Demo app
This repo ships with a full demo:
```bash
python demo_app/setup_demo.py
python demo_app/manage.py runserver
```
- Main: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/ (login: `admin` / `admin123`)

See `demo_app/README.md` for details.
