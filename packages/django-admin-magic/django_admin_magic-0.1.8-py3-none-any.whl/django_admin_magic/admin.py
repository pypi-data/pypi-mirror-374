from django.apps import apps as django_apps

from .conf import app_settings
from .utils import autoreg_disabled


def _perform_registration_if_configured():
    """
    Perform admin registration based on settings during Django admin autodiscover.

    This runs when django.contrib.admin.autodiscover imports this module.
    It ensures models are registered before AdminSite URL patterns are constructed
    so app_list URLs include all relevant app labels.
    """
    # Respect disabled contexts (e.g., migrations) and admin not installed
    if autoreg_disabled():
        return

    # Avoid duplicate work if registrar already set (e.g., via AppConfig.ready)
    config = django_apps.get_app_config("django_admin_magic")
    if getattr(config, "registrar", None) is not None:
        return

    # Choose appropriate registrar based on polymorphic availability
    if "polymorphic" in django_apps.app_configs:
        from .registrar import PolymorphicAdminModelRegistrar as Registrar
    else:
        from .registrar import AdminModelRegistrar as Registrar

    # Priority: AUTO_DISCOVER_ALL_APPS -> APP_LABELS -> APP_LABEL
    if getattr(app_settings, "AUTO_DISCOVER_ALL_APPS", False):
        config.registrar = Registrar.register_all_discovered_apps()
        return

    if getattr(app_settings, "APP_LABELS", []):
        config.registrar = Registrar.register_apps(app_settings.APP_LABELS)
        return

    app_label = getattr(app_settings, "APP_LABEL", None)
    if app_label:
        if isinstance(app_label, list):
            config.registrar = Registrar.register_apps(app_label)
        else:
            config.registrar = Registrar.register_app(app_label)
        return

    # Nothing configured; leave registrar unset


# Execute at import time during admin.autodiscover
_perform_registration_if_configured()
