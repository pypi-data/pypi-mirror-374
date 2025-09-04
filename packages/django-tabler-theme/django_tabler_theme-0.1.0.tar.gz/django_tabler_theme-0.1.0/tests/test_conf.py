import pytest
from django_tabler_theme.conf import get_setting, DEFAULTS


def test_get_setting_defaults():
    """Test that get_setting returns default values when no custom settings."""
    for key, expected_value in DEFAULTS.items():
        assert get_setting(key) == expected_value


@pytest.mark.django_db
def test_get_setting_custom_values(settings):
    """Test that get_setting returns custom values when provided."""
    custom_settings = {
        "BRAND_NAME": "Test App",
        "USE_CDN": False,
        "NAVBAR_COLOR": "danger",
    }
    settings.TABLER_THEME = custom_settings

    assert get_setting("BRAND_NAME") == "Test App"
    assert get_setting("USE_CDN") is False
    assert get_setting("NAVBAR_COLOR") == "danger"

    # Should still return defaults for unspecified keys
    assert get_setting("DARK_MODE") == DEFAULTS["DARK_MODE"]
    assert get_setting("TABLER_VERSION") == DEFAULTS["TABLER_VERSION"]


@pytest.mark.django_db
def test_get_setting_partial_custom(settings):
    """Test that get_setting properly merges custom and default settings."""
    settings.TABLER_THEME = {
        "BRAND_NAME": "Partial Custom",
        # Other settings should use defaults
    }

    assert get_setting("BRAND_NAME") == "Partial Custom"
    assert get_setting("LOGO_URL") == DEFAULTS["LOGO_URL"]
    assert get_setting("USE_CDN") == DEFAULTS["USE_CDN"]
