import re

import pytest
from django.contrib import admin
from django.urls import reverse

from django_admin_magic.mixins import ListAdmin

from .models import ForeignKeyModel, M2MTarget, WithThrough


@pytest.mark.django_db
def test_m2m_list_display_includes_m2m_field(admin_site, simple_model_instance, complex_model_instance):
    # Arrange: create instance with one m2m
    fk = ForeignKeyModel.objects.create(
        simple_foreign_key=simple_model_instance,
        complex_foreign_key=complex_model_instance,
        one_to_one=simple_model_instance,
        name="Has M2M",
    )
    fk.many_to_many.add(simple_model_instance)

    # Act: build admin and locate the m2m display callable
    admin_instance = ListAdmin(ForeignKeyModel, admin_site)
    display_funcs = [f for f in admin_instance.list_display if callable(f)]
    m2m_func = None
    for func in display_funcs:
        if getattr(func, "short_description", "") == "Many To Many":
            m2m_func = func
            break

    assert m2m_func is not None, "Expected m2m display function to be present in list_display"

    # Assert: output contains a link to the SimpleModel change page
    html = str(m2m_func(fk))
    expected_href = reverse("admin:tests_simplemodel_change", args=[simple_model_instance.pk])
    assert expected_href in html


@pytest.mark.django_db
def test_m2m_list_display_clipping_limit(settings, admin_site, foreign_key_model_instance):
    # Limit to 3 items for this test
    settings.AUTO_ADMIN_M2M_LIST_MAX_ITEMS = 3

    fk = foreign_key_model_instance
    # Ensure at least 5 related items
    for i in range(4):
        fk.many_to_many.create(name=f"Rel-{i}")

    admin_instance = ListAdmin(ForeignKeyModel, admin_site)
    m2m_func = next(f for f in admin_instance.list_display if callable(f) and getattr(f, "short_description", "") == "Many To Many")

    html = str(m2m_func(fk))
    # Expect exactly 3 links
    assert html.count('<a href="') == 3
    assert "..." in html


@pytest.mark.django_db
def test_m2m_list_display_disabled(settings, admin_site):
    settings.AUTO_ADMIN_M2M_LIST_ENABLED = False
    admin_instance = ListAdmin(ForeignKeyModel, admin_site)
    assert all(getattr(func, "short_description", "") != "Many To Many" for func in admin_instance.list_display if callable(func))


@pytest.mark.django_db
def test_m2m_through_relation_traverses_to_target(admin_site):
    a = WithThrough.objects.create(name="A")
    t1 = M2MTarget.objects.create(name="T1")
    t2 = M2MTarget.objects.create(name="T2")
    # Use through to connect
    a.targets.add(t1)
    a.targets.add(t2)

    admin_instance = ListAdmin(WithThrough, admin_site)
    m2m_func = next(f for f in admin_instance.list_display if callable(f) and getattr(f, "short_description", "") == "Targets")
    html = str(m2m_func(a))

    # Should link to target admin pages
    href1 = reverse("admin:tests_m2mtarget_change", args=[t1.pk])
    href2 = reverse("admin:tests_m2mtarget_change", args=[t2.pk])
    assert href1 in html and href2 in html


@pytest.mark.django_db
def test_m2m_custom_display_attribute(settings, admin_site):
    settings.AUTO_ADMIN_M2M_LIST_DISPLAY_ATTR = "name"
    a = WithThrough.objects.create(name="A")
    t = M2MTarget.objects.create(name="PrettyName")
    a.targets.add(t)

    admin_instance = ListAdmin(WithThrough, admin_site)
    m2m_func = next(f for f in admin_instance.list_display if callable(f) and getattr(f, "short_description", "") == "Targets")
    html = str(m2m_func(a))
    assert "PrettyName" in html
    # Ensure we didn't fall back to __str__ which prefixes with "Target-"
    assert "Target-" not in html


