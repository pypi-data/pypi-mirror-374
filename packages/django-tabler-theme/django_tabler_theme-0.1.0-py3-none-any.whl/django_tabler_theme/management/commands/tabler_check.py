from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
import os


class Command(BaseCommand):
    help = "Check django-tabler-theme configuration and setup"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed information",
        )
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Attempt to fix common issues",
        )

    def handle(self, *args, **options):
        self.verbose = options.get("verbose", False)
        self.fix_issues = options.get("fix", False)

        self.stdout.write(
            self.style.SUCCESS("🔍 Django Tabler Theme Configuration Check")
        )
        self.stdout.write("")

        issues_found = 0

        # Check all configuration aspects
        issues_found += self.check_installed_apps()
        issues_found += self.check_context_processors()
        issues_found += self.check_templates_config()
        issues_found += self.check_static_files()
        issues_found += self.check_tabler_theme_settings()
        issues_found += self.check_template_files()
        issues_found += self.check_urls()

        # Summary
        self.stdout.write("")
        if issues_found == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "✅ All checks passed! Your django-tabler-theme setup looks good."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Found {issues_found} issue(s) that need attention."
                )
            )
            if not self.fix_issues:
                self.stdout.write("Run with --fix to attempt automatic fixes.")

    def check_installed_apps(self):
        """Check if django-tabler-theme is in INSTALLED_APPS."""
        self.stdout.write("📦 Checking INSTALLED_APPS...")

        if "django_tabler_theme" in settings.INSTALLED_APPS:
            self.stdout.write("  ✅ django_tabler_theme found in INSTALLED_APPS")
            return 0
        else:
            self.stdout.write(
                self.style.ERROR("  ❌ django_tabler_theme not in INSTALLED_APPS")
            )
            if self.fix_issues:
                self.stdout.write("  🔧 Auto-fix not available for INSTALLED_APPS")
            else:
                self.stdout.write(
                    "  💡 Add 'django_tabler_theme' to INSTALLED_APPS in settings.py"
                )
            return 1

    def check_context_processors(self):
        """Check if context processor is configured."""
        self.stdout.write("🔄 Checking context processors...")

        context_processors = []
        for template_config in settings.TEMPLATES:
            if "context_processors" in template_config.get("OPTIONS", {}):
                context_processors.extend(
                    template_config["OPTIONS"]["context_processors"]
                )

        required_processor = "django_tabler_theme.context_processors.tabler_settings"

        if required_processor in context_processors:
            self.stdout.write("  ✅ Context processor configured correctly")
            return 0
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"  ❌ Context processor not configured: {required_processor}"
                )
            )
            if self.fix_issues:
                self.stdout.write("  🔧 Auto-fix not available for context processors")
            else:
                self.stdout.write(
                    f"  💡 Add '{required_processor}' to TEMPLATES context_processors"
                )
            return 1

    def check_templates_config(self):
        """Check TEMPLATES configuration."""
        self.stdout.write("📄 Checking TEMPLATES configuration...")

        issues = 0

        if not hasattr(settings, "TEMPLATES") or not settings.TEMPLATES:
            self.stdout.write(self.style.ERROR("  ❌ TEMPLATES setting not configured"))
            return 1

        # Check if at least one backend is DjangoTemplates
        django_backend_found = False
        for template_config in settings.TEMPLATES:
            if (
                template_config.get("BACKEND")
                == "django.template.backends.django.DjangoTemplates"
            ):
                django_backend_found = True

                # Check if APP_DIRS is True
                if template_config.get("APP_DIRS", False):
                    self.stdout.write("  ✅ APP_DIRS is enabled")
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            "  ⚠️  APP_DIRS is disabled - may cause template loading issues"
                        )
                    )
                    issues += 1

        if django_backend_found:
            self.stdout.write("  ✅ Django template backend configured")
        else:
            self.stdout.write(
                self.style.ERROR("  ❌ Django template backend not found")
            )
            issues += 1

        return issues

    def check_static_files(self):
        """Check static files configuration."""
        self.stdout.write("📁 Checking static files configuration...")

        issues = 0

        if hasattr(settings, "STATIC_URL"):
            self.stdout.write(f"  ✅ STATIC_URL configured: {settings.STATIC_URL}")
        else:
            self.stdout.write(self.style.ERROR("  ❌ STATIC_URL not configured"))
            issues += 1

        # Check if django.contrib.staticfiles is in INSTALLED_APPS
        if "django.contrib.staticfiles" in settings.INSTALLED_APPS:
            self.stdout.write("  ✅ django.contrib.staticfiles found in INSTALLED_APPS")
        else:
            self.stdout.write(
                self.style.WARNING(
                    "  ⚠️  django.contrib.staticfiles not in INSTALLED_APPS"
                )
            )
            issues += 1

        return issues

    def check_tabler_theme_settings(self):
        """Check TABLER_THEME settings."""
        self.stdout.write("⚙️  Checking TABLER_THEME configuration...")

        if not hasattr(settings, "TABLER_THEME"):
            self.stdout.write(
                self.style.WARNING("  ⚠️  TABLER_THEME not configured (using defaults)")
            )
            if self.verbose:
                self.stdout.write(
                    "  💡 Consider adding TABLER_THEME settings for customization"
                )
            return 0

        theme_config = getattr(settings, "TABLER_THEME")

        if not isinstance(theme_config, dict):
            self.stdout.write(
                self.style.ERROR("  ❌ TABLER_THEME must be a dictionary")
            )
            return 1

        self.stdout.write("  ✅ TABLER_THEME configuration found")

        if self.verbose:
            self.stdout.write("  📋 Current configuration:")
            for key, value in theme_config.items():
                self.stdout.write(f"    {key}: {value}")

        # Check for common settings
        if "BRAND_NAME" in theme_config:
            self.stdout.write(f'    ✅ Brand name: {theme_config["BRAND_NAME"]}')

        if "LOGO_URL" in theme_config:
            self.stdout.write(f'    ✅ Logo configured: {theme_config["LOGO_URL"]}')

        if "USE_CDN" in theme_config:
            cdn_status = "enabled" if theme_config["USE_CDN"] else "disabled"
            self.stdout.write(f"    ✅ CDN: {cdn_status}")

        return 0

    def check_template_files(self):
        """Check if base templates exist and are accessible."""
        self.stdout.write("📑 Checking template files...")

        issues = 0
        templates_to_check = [
            "tabler_theme/base.html",
        ]

        for template_name in templates_to_check:
            try:
                get_template(template_name)
                self.stdout.write(f"  ✅ Template accessible: {template_name}")
            except TemplateDoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Template not found: {template_name}")
                )
                issues += 1

        # Check for custom base template
        try:
            get_template("base.html")
            self.stdout.write("  ✅ Custom base.html template found")
        except TemplateDoesNotExist:
            self.stdout.write(
                self.style.WARNING("  ⚠️  No custom base.html template found")
            )
            if self.verbose:
                self.stdout.write(
                    "  💡 Consider creating a base.html that extends tabler_theme/base.html"
                )

        return issues

    def check_urls(self):
        """Check URL configuration."""
        self.stdout.write("🔗 Checking URL configuration...")

        issues = 0

        # Try to import the root URL configuration
        try:
            from django.urls import reverse
            from django.urls.exceptions import NoReverseMatch

            # Try to reverse some common URLs
            try:
                reverse("admin:index")
                self.stdout.write("  ✅ Admin URLs accessible")
            except NoReverseMatch:
                self.stdout.write(self.style.WARNING("  ⚠️  Admin URLs not configured"))
                if self.verbose:
                    self.stdout.write(
                        "  💡 Consider adding django.contrib.admin.urls to your URL configuration"
                    )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ URL configuration error: {e}"))
            issues += 1

        return issues

    def check_version_compatibility(self):
        """Check Django version compatibility."""
        self.stdout.write("🐍 Checking Django version compatibility...")

        import django

        django_version = django.get_version()

        # django-tabler-theme requires Django 3.2+
        major, minor = django.VERSION[:2]

        if major >= 4 or (major == 3 and minor >= 2):
            self.stdout.write(f"  ✅ Django version compatible: {django_version}")
            return 0
        else:
            self.stdout.write(
                self.style.ERROR(f"  ❌ Django version not supported: {django_version}")
            )
            self.stdout.write("  💡 django-tabler-theme requires Django 3.2 or higher")
            return 1
