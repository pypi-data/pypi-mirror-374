# Configuration

Django Admin Magic reads settings via the `AUTO_ADMIN_` prefix. These map to defaults in `django_admin_magic.defaults`.

## Core selection
- **AUTO_ADMIN_APP_LABEL**: string or list. App(s) to register. Default: `None`.
- **AUTO_ADMIN_APP_LABELS**: list of app labels. Default: `[]`.
- **AUTO_ADMIN_AUTO_DISCOVER_ALL_APPS**: bool. Discover all installed apps with models. Default: `False`.
- **AUTO_ADMIN_DISABLED**: bool. Global kill switch. Default: `False`.

## Safety and context
- **AUTO_ADMIN_SKIP_COMMANDS**: list. Management commands that disable auto-registration (e.g. `makemigrations`, `migrate`). Default: `["makemigrations", "migrate"]`.
- **AUTO_ADMIN_SKIP_IF_ADMIN_NOT_INSTALLED**: bool. Skip when `django.contrib.admin` is not in `INSTALLED_APPS`. Default: `True`.
- Env overrides: set `DJANGO_ADMIN_MAGIC_DISABLE=1` or `AUTO_ADMIN_DISABLE=1` to disable.

## Admin defaults and heuristics
- **AUTO_ADMIN_DEFAULT_EXCLUDED_TERMS**: list of substrings filtered from `list_display` (e.g. `"_ptr"`, `"uuid"`, `"id"`, `"pk"`, `"search"`).
- **AUTO_ADMIN_DEFAULT_DO_NOT_REGISTER_FILTER_STRING_LIST**: model name substrings that prevent registration (e.g. `"Historical"`).
- **AUTO_ADMIN_ADMIN_TUPLE_ATTRIBUTES_TO_LIST**: attributes coerced to lists so they can be mutated (default: `list_display`, `list_filter`, `search_fields`, `readonly_fields`).
- **AUTO_ADMIN_REORDER_LINKIFY_FIELDS**: bool. Avoids a linkified field being first in changelist to prevent checkbox conflicts. Default: `True`.

## Registrar helpers
You can bypass settings and specify apps directly from `admin.py` using:
```python
from django_admin_magic.utils import (
    create_auto_admin_registrar,
    create_auto_admin_registrar_for_apps,
    create_auto_admin_registrar_for_all_apps,
)
```

These utilities respect the same safety checks as settings.
