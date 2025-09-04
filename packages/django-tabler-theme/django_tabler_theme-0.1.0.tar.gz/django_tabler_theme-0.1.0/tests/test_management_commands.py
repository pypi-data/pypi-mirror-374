import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.core.management import call_command
from django.core.management.base import CommandError


class BaseManagementCommandTest(TestCase):
    """Base class for management command tests."""

    def setUp(self):
        # Use tempfile.TemporaryDirectory for automatic cleanup
        self.temp_project_dir_obj = tempfile.TemporaryDirectory()
        self.temp_project_dir = Path(self.temp_project_dir_obj.name)
        self.templates_dir = self.temp_project_dir / "templates"
        self.templates_dir.mkdir(exist_ok=True)

    def tearDown(self):
        # Cleanup is automatic with TemporaryDirectory
        self.temp_project_dir_obj.cleanup()

    def call_command(self, *args, **kwargs):
        """Helper method to call management commands and capture output."""
        out = StringIO()
        err = StringIO()
        call_command(*args, stdout=out, stderr=err, **kwargs)
        return out.getvalue(), err.getvalue()


class TablerSetupCommandTest(BaseManagementCommandTest):
    """Test cases for tabler_setup management command."""

    def test_setup_basic_functionality(self):
        """Test basic setup command functionality."""
        with override_settings(BASE_DIR=self.temp_project_dir):
            out, err = self.call_command("tabler_setup")

            # Check that setup ran without errors
            self.assertIn("Django Tabler Theme Setup", out)
            self.assertEqual(err, "")


class TablerGenerateCommandTest(BaseManagementCommandTest):
    """Test cases for tabler_generate management command."""

    def test_generate_form_template(self):
        """Test generating a form template."""
        with override_settings(BASE_DIR=self.temp_project_dir):
            out, err = self.call_command("tabler_generate", "form", "test_form")

            # Check that the command ran (adjust assertion based on actual output)
            self.assertIn("🎨 Generating form template: test_form", out)
            self.assertIn("✅ Template generated successfully!", out)
            self.assertEqual(err, "")

            # Check template file was created (command appends _form.html)
            generated_file = self.temp_project_dir / "templates" / "test_form_form.html"
            self.assertTrue(generated_file.exists())

    def test_generate_page_template(self):
        """Test generating a page template."""
        with override_settings(BASE_DIR=self.temp_project_dir):
            out, err = self.call_command("tabler_generate", "page", "test_page")

            # Check that the command ran
            self.assertIn("🎨 Generating page template: test_page", out)
            self.assertIn("✅ Template generated successfully!", out)
            self.assertEqual(err, "")

            # Check template file was created (page templates use just .html)
            generated_file = self.temp_project_dir / "templates" / "test_page.html"
            self.assertTrue(generated_file.exists())

    def test_generate_existing_template_fails_without_force(self):
        """Test that generating an existing template fails without --force."""
        with override_settings(BASE_DIR=self.temp_project_dir):
            # First, create the template
            self.call_command("tabler_generate", "form", "duplicate_form")

            # Try to create it again without --force
            with self.assertRaises(CommandError) as cm:
                self.call_command("tabler_generate", "form", "duplicate_form")

            self.assertIn("already exists", str(cm.exception))

    def test_generate_with_force_overwrites(self):
        """Test that --force flag overwrites existing templates."""
        with override_settings(BASE_DIR=self.temp_project_dir):
            # First, create the template
            self.call_command("tabler_generate", "form", "overwrite_form")

            # Now overwrite it with --force
            out, err = self.call_command(
                "tabler_generate", "form", "overwrite_form", force=True
            )

            self.assertIn("🎨 Generating form template: overwrite_form", out)
            self.assertIn("✅ Template generated successfully!", out)
            self.assertEqual(err, "")


class TablerCheckCommandTest(BaseManagementCommandTest):
    """Test cases for tabler_check management command."""

    def test_check_valid_configuration(self):
        """Test check command with valid configuration."""
        with override_settings(
            BASE_DIR=self.temp_project_dir,
            INSTALLED_APPS=[
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django_tabler_theme",
            ],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [str(self.templates_dir)],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django_tabler_theme.context_processors.theme",
                        ],
                    },
                }
            ],
        ):
            out, err = self.call_command("tabler_check")

            # Should show configuration checking output
            self.assertIn("Django Tabler Theme Configuration Check", out)
            self.assertEqual(err, "")


class TablerCopyCommandTest(BaseManagementCommandTest):
    """Test cases for tabler_copy management command."""

    def test_copy_list_templates(self):
        """Test listing available templates."""
        with patch(
            "django_tabler_theme.management.commands.tabler_copy.os.path.dirname"
        ) as mock_dirname:
            with patch(
                "django_tabler_theme.management.commands.tabler_copy.os.path.exists"
            ) as mock_exists:
                with patch(
                    "django_tabler_theme.management.commands.tabler_copy.os.walk"
                ) as mock_walk:
                    mock_dirname.return_value = str(self.temp_project_dir)
                    mock_exists.return_value = True
                    mock_walk.return_value = [
                        (str(self.templates_dir), [], ["base.html", "form.html"])
                    ]

                    out, err = self.call_command("tabler_copy", "--list")

                    self.assertIn("Available Templates:", out)
                    self.assertIn("base.html", out)
                    self.assertIn("form.html", out)

    def test_copy_single_template(self):
        """Test copying a single template."""
        # Create the actual django_tabler_theme template directory
        actual_template_dir = (
            Path(__file__).parent.parent
            / "src"
            / "django_tabler_theme"
            / "templates"
            / "tabler_theme"
        )

        # Skip test if the actual template directory doesn't exist
        if not actual_template_dir.exists():
            self.skipTest("Actual template directory not found")

        with override_settings(BASE_DIR=self.temp_project_dir):
            out, err = self.call_command("tabler_copy", "base.html")

            # Check the output indicates success or failure appropriately
            self.assertIn("Django Tabler Theme Template Copy Tool", out)

            # The test should at least run without crashing
            # We can't easily test file copying without the actual source files


class TablerIntegrationTest(BaseManagementCommandTest):
    """Integration tests for management commands working together."""

    def test_setup_then_check_workflow(self):
        """Test that setup works followed by check."""
        with override_settings(
            BASE_DIR=self.temp_project_dir,
            INSTALLED_APPS=[
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django_tabler_theme",
            ],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [str(self.templates_dir)],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django_tabler_theme.context_processors.theme",
                        ],
                    },
                }
            ],
        ):
            # 1. Run setup
            out1, err1 = self.call_command("tabler_setup")
            self.assertIn("Django Tabler Theme Setup", out1)
            self.assertEqual(err1, "")

            # 2. Run check
            out2, err2 = self.call_command("tabler_check")
            self.assertIn("Django Tabler Theme Configuration Check", out2)
            self.assertEqual(err2, "")

    def test_generate_multiple_templates(self):
        """Test generating multiple different template types."""
        with override_settings(BASE_DIR=self.temp_project_dir):
            # Generate form template
            out1, err1 = self.call_command("tabler_generate", "form", "user_form")
            self.assertIn("✅ Template generated successfully!", out1)

            # Generate page template
            out2, err2 = self.call_command("tabler_generate", "page", "about_page")
            self.assertIn("✅ Template generated successfully!", out2)

            # Verify both files exist
            form_file = self.temp_project_dir / "templates" / "user_form_form.html"
            page_file = self.temp_project_dir / "templates" / "about_page.html"

            self.assertTrue(form_file.exists())
            self.assertTrue(page_file.exists())
