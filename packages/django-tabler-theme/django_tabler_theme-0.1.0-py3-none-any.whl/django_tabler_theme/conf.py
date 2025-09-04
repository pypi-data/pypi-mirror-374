from django.conf import settings as dj_settings

DEFAULTS = {
    "BRAND_NAME": "Your Brand",
    "LOGO_URL": None,  # e.g. "/static/logo.svg"
    "LOGO_URL_DARK": None,  # Optional dark mode logo
    "LOGO_WIDTH": "110",  # Logo width in pixels
    "LOGO_HEIGHT": "32",  # Logo height in pixels
    "LOGO_ALT": None,  # Logo alt text (defaults to BRAND_NAME)
    "USE_CDN": True,  # If False, serve local assets under static/tabler_theme/
    "NAVBAR_COLOR": "primary",  # Tabler color name
    "DARK_MODE": False,
    "TABLER_VERSION": "latest",  # update as needed
    "USE_SIDEBAR": False,  # Enable vertical sidebar navigation
}


def get_setting(key):
    return getattr(dj_settings, "TABLER_THEME", {}).get(key, DEFAULTS[key])
