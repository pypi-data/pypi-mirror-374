import pytest
from django.template.loader import render_to_string
from django.test.client import RequestFactory
from django.test import override_settings
from django.template import Context, RequestContext


@pytest.mark.django_db
def test_base_template_renders():
    """Test that the base template renders correctly."""
    rf = RequestFactory()
    request = rf.get("/")
    html = render_to_string(
        "tabler_theme/base.html", context={"request": request}, request=request
    )
    assert "<title>" in html


@pytest.mark.django_db
def test_context_processor_injects_expected_keys():
    """Test that the context processor injects all expected Tabler settings."""
    rf = RequestFactory()
    request = rf.get("/")
    html = render_to_string(
        "tabler_theme/base.html", context={"request": request}, request=request
    )

    # Check that default brand name is rendered
    assert "Your Brand" in html

    # Check that Tabler CSS CDN link is present
    assert "cdn.jsdelivr.net/npm/@tabler/core" in html

    # Check that icons CDN link is present
    assert "tabler-icons" in html


@pytest.mark.django_db
@override_settings(
    TABLER_THEME={
        "BRAND_NAME": "Test Brand",
        "USE_CDN": False,
        "NAVBAR_COLOR": "success",
    }
)
def test_custom_tabler_settings():
    """Test that custom TABLER_THEME settings are properly used."""
    rf = RequestFactory()
    request = rf.get("/")
    html = render_to_string(
        "tabler_theme/base.html", context={"request": request}, request=request
    )

    # Check custom brand name
    assert "Test Brand" in html

    # Check that local assets are used instead of CDN
    assert "cdn.jsdelivr.net" not in html
    assert "tabler_theme/tabler.min.css" in html


@pytest.mark.django_db
def test_topnav_template_renders():
    """Test that the top navigation elements render correctly in base template."""
    rf = RequestFactory()
    request = rf.get("/")

    # Test that base template contains navbar elements
    html = render_to_string(
        "tabler_theme/base.html", context={"request": request}, request=request
    )

    assert "navbar" in html
    assert "navbar-toggler" in html
    assert "Your Brand" in html


@pytest.mark.django_db
def test_sidebar_template_renders():
    """Test that the sidebar elements render correctly in base template when enabled."""
    rf = RequestFactory()
    request = rf.get("/")

    # Test base template with sidebar enabled - need to include the context processor variables
    with override_settings(TABLER_THEME={"USE_SIDEBAR": True}):
        from django_tabler_theme.context_processors import tabler_settings

        context = tabler_settings(request)
        html = render_to_string(
            "tabler_theme/base.html", context=context, request=request
        )

        assert "navbar-vertical" in html


@pytest.mark.django_db
def test_messages_template_renders():
    """Test that messages are handled correctly in base template."""
    rf = RequestFactory()

    # Test base template renders without messages
    html = render_to_string("tabler_theme/base.html", {"messages": []})

    # Should render without error and contain basic structure
    assert "<!DOCTYPE html>" in html
    assert "<body" in html
