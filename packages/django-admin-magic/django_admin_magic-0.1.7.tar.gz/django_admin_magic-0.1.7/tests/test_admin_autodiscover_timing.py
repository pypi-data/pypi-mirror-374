import pytest
from django.contrib import admin
from django.test.utils import override_settings
from django.urls import reverse


@pytest.mark.django_db
def test_admin_app_list_reverse_with_global_autodiscover():
    """
    Ensure that when relying on global auto-discover mode, admin URLs include
    the app_list entry for the tests app so reverse('admin:app_list', {'app_label': 'tests'}) works.
    """
    with override_settings(
        AUTO_ADMIN_APP_LABEL=None,
        AUTO_ADMIN_APP_LABELS=[],
        AUTO_ADMIN_AUTO_DISCOVER_ALL_APPS=True,
    ):
        # Force admin autodiscover to import admin modules and build URL patterns
        admin.autodiscover()

        # Should be able to reverse the app_list URL for the tests app
        url = reverse("admin:app_list", kwargs={"app_label": "tests"})
        assert url.endswith("/admin/tests/")


