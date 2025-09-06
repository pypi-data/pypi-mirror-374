# Utilities

## linkify(field_name)
Turns a foreign key in `list_display` into a clickable link to the related object's admin change page.
```python
from django_admin_magic.utils import linkify

MyModelAdmin = registrar.return_admin_class_for_model(MyModel)
MyModelAdmin.list_display += [linkify("parent")]
```
- Sets `short_description` and `admin_order_field` automatically
- Falls back to plain text if the related model is not registered in admin

## linkify_gfk(field_name)
For `GenericForeignKey` fields, generates a link to the target object's admin change page when possible, otherwise displays a readable fallback.

## TimeLimitedPaginator
A custom paginator that avoids long-running `COUNT(*)` queries by setting a short statement timeout on PostgreSQL and providing a safe fallback.

Configure on your own `ModelAdmin` if you need it directly:
```python
from django_admin_magic.utils import TimeLimitedPaginator

class MyAdmin(admin.ModelAdmin):
    paginator = TimeLimitedPaginator
```

This paginator is also applied by default through the admin mixins.

## linkify_m2m(field_name)
Render a ManyToMany field in the changelist as a comma-separated list of linkified related objects.

```python
from django_admin_magic.utils import linkify_m2m

MyModelAdmin = registrar.return_admin_class_for_model(MyModel)
MyModelAdmin.list_display += [linkify_m2m("tags")]
```

- Respects configuration: `AUTO_ADMIN_M2M_LIST_MAX_ITEMS`, `AUTO_ADMIN_M2M_LIST_DISPLAY_ATTR`
- Clips with `...` when more than the configured limit
- Works with explicit `through` models (shows the end objects)
