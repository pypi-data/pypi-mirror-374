from .conf import get_setting


def tabler_settings(request):
    return {
        "TABLER_BRAND_NAME": get_setting("BRAND_NAME"),
        "TABLER_LOGO_URL": get_setting("LOGO_URL"),
        "TABLER_LOGO_URL_DARK": get_setting("LOGO_URL_DARK"),
        "TABLER_LOGO_WIDTH": get_setting("LOGO_WIDTH"),
        "TABLER_LOGO_HEIGHT": get_setting("LOGO_HEIGHT"),
        "TABLER_LOGO_ALT": get_setting("LOGO_ALT") or get_setting("BRAND_NAME"),
        "TABLER_USE_CDN": get_setting("USE_CDN"),
        "TABLER_NAVBAR_COLOR": get_setting("NAVBAR_COLOR"),
        "TABLER_DARK_MODE": get_setting("DARK_MODE"),
        "TABLER_VERSION": get_setting("TABLER_VERSION"),
        "TABLER_USE_SIDEBAR": get_setting("USE_SIDEBAR"),
    }
