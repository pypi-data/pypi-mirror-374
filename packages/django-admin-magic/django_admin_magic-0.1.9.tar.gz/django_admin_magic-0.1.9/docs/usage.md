# Usage

After creating a registrar, you can customize admin classes at runtime.

## Get the live admin instance for a model
```python
from django.apps import apps

registrar = apps.get_app_config("django_admin_magic").registrar
MyModelAdmin = registrar.return_admin_class_for_model(MyModel)
```

## Display columns
Append fields to the end:
```python
registrar.append_list_display(MyModel, ["status", "created_at"]) 
```

Prepend fields to the start:
```python
registrar.prepend_list_display(MyModel, ["name"]) 
```

Remove fields:
```python
registrar.remove_list_display(MyModel, ["obsolete_field"]) 
```

## Filters and search
```python
registrar.append_filter_display(MyModel, ["is_active", "category"]) 
registrar.add_search_fields(MyModel, ["name", "description"]) 
```

## Query optimization
```python
# Select all FKs
registrar.update_list_select_related(MyModel, True)
# Or specific relationships
registrar.update_list_select_related(MyModel, ["author", "category"]) 
```

## Adding admin methods
Add an action:
```python
def mark_as_special(modeladmin, request, queryset):
    queryset.update(is_special=True)

registrar.add_admin_method(
    MyModel,
    "mark_as_special",
    mark_as_special,
    short_description="Mark selected as special",
    is_action=True,
)
```

Add a display method:
```python
def display_upper_name(admin_instance, obj):
    return obj.name.upper()

action = registrar.add_admin_method(
    MyModel,
    "upper_name",
    display_upper_name,
    short_description="Upper name",
)
```

All changes are synced to the live ModelAdmin instance immediately.
