import pytest
from django.test.client import RequestFactory
from django_tabler_theme.context_processors import tabler_settings


def test_context_processor_default_settings():
    """Test that context processor returns default settings."""
    rf = RequestFactory()
    request = rf.get("/")

    context = tabler_settings(request)

    expected_keys = [
        "TABLER_BRAND_NAME",
        "TABLER_LOGO_URL",
        "TABLER_USE_CDN",
        "TABLER_NAVBAR_COLOR",
        "TABLER_DARK_MODE",
        "TABLER_VERSION",
    ]

    for key in expected_keys:
        assert key in context

    # Check default values
    assert context["TABLER_BRAND_NAME"] == "Your Brand"
    assert context["TABLER_LOGO_URL"] is None
    assert context["TABLER_USE_CDN"] is True
    assert context["TABLER_NAVBAR_COLOR"] == "primary"
    assert context["TABLER_DARK_MODE"] is False
    assert context["TABLER_VERSION"] == "latest"


@pytest.mark.django_db
def test_context_processor_custom_settings(settings):
    """Test that context processor uses custom settings when provided."""
    settings.TABLER_THEME = {
        "BRAND_NAME": "Custom Brand",
        "USE_CDN": False,
        "NAVBAR_COLOR": "success",
        "DARK_MODE": True,
    }

    rf = RequestFactory()
    request = rf.get("/")

    context = tabler_settings(request)

    assert context["TABLER_BRAND_NAME"] == "Custom Brand"
    assert context["TABLER_USE_CDN"] is False
    assert context["TABLER_NAVBAR_COLOR"] == "success"
    assert context["TABLER_DARK_MODE"] is True
    # Should still use default for unspecified settings
    assert context["TABLER_VERSION"] == "latest"
