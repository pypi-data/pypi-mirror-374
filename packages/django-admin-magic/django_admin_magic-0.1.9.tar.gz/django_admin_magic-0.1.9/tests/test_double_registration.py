import pytest
from django.contrib import admin

from django_admin_magic.registrar import AdminModelRegistrar

from .models import SimpleModel


@pytest.mark.django_db
def test_manual_double_register_raises_already_registered(admin_site):
    """Emulate double-registration: registering the same model twice raises AlreadyRegistered."""
    class DummyAdmin(admin.ModelAdmin):
        pass

    from django.contrib.admin.exceptions import AlreadyRegistered

    # In test environment, SimpleModel is already auto-registered.
    # Attempting to register again should raise AlreadyRegistered (emulates third-party admin).
    with pytest.raises(AlreadyRegistered):
        admin_site.register(SimpleModel, DummyAdmin)


@pytest.mark.django_db
def test_auto_admin_skips_when_model_already_registered(admin_site):
    """If a model is already registered, auto-admin should not re-register or error."""
    class PreRegisteredAdmin(admin.ModelAdmin):
        pass

    # Simulate third-party admin.py by replacing existing registration
    try:
        admin_site.unregister(SimpleModel)
    except Exception:
        pass
    admin_site.register(SimpleModel, PreRegisteredAdmin)

    try:
        # Now run auto-admin; should not raise
        AdminModelRegistrar.register_apps(["tests"])  # should skip SimpleModel

        # Ensure the registered admin remains the pre-registered one
        instance = admin_site._registry[SimpleModel]
        assert isinstance(instance, PreRegisteredAdmin)
    finally:
        # Restore default auto-admin registration for isolation
        try:
            admin_site.unregister(SimpleModel)
        except Exception:
            pass
        AdminModelRegistrar.register_apps(["tests"])  # restore


