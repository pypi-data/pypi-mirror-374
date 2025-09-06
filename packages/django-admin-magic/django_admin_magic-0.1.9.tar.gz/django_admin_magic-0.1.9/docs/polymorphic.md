# Polymorphic Models

If `django-polymorphic` is installed, Django Admin Magic adapts automatically:

- Parent models use `PolymorphicParentListAdmin`, listing the parent and all child types
- Child models use `PolymorphicChildListAdmin`
- Child classes are discovered dynamically using Python subclass inspection

## Usage
No special configuration is required. Register your app(s) normally; the correct admin classes are chosen for you.

```python
from django_admin_magic.utils import create_auto_admin_registrar
registrar = create_auto_admin_registrar("my_app")
```

You can customize list displays, filters, search, and actions the same way as for non-polymorphic models.

