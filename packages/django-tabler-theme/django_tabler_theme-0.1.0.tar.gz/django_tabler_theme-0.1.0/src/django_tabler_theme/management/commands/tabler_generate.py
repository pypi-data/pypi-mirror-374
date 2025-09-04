from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps
from django.template.loader import render_to_string
import os


class Command(BaseCommand):
    help = "Generate templates and components for django-tabler-theme"

    def add_arguments(self, parser):
        parser.add_argument(
            "type",
            choices=["form", "table", "dashboard", "page", "auth"],
            help="Type of template to generate",
        )
        parser.add_argument(
            "name",
            type=str,
            help="Name of the template/component",
        )
        parser.add_argument(
            "--app",
            type=str,
            help="App to create template in",
        )
        parser.add_argument(
            "--model",
            type=str,
            help="Model name for form/table templates",
        )
        parser.add_argument(
            "--fields",
            type=str,
            help="Comma-separated list of fields",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing files",
        )

    def handle(self, *args, **options):
        self.template_type = options["type"]
        self.name = options["name"]
        self.app_name = options.get("app")
        self.model_name = options.get("model")
        self.fields = (
            options.get("fields", "").split(",") if options.get("fields") else []
        )
        self.force = options.get("force")

        self.stdout.write(
            self.style.SUCCESS(
                f"🎨 Generating {self.template_type} template: {self.name}"
            )
        )

        # Get templates directory
        if self.app_name:
            try:
                apps.get_app_config(self.app_name)
                self.templates_dir = os.path.join(
                    settings.BASE_DIR, "templates", self.app_name
                )
            except LookupError:
                raise CommandError(f'App "{self.app_name}" not found')
        else:
            self.templates_dir = os.path.join(settings.BASE_DIR, "templates")

        os.makedirs(self.templates_dir, exist_ok=True)

        # Generate based on type
        if self.template_type == "form":
            self.generate_form_template()
        elif self.template_type == "table":
            self.generate_table_template()
        elif self.template_type == "dashboard":
            self.generate_dashboard_template()
        elif self.template_type == "page":
            self.generate_page_template()
        elif self.template_type == "auth":
            self.generate_auth_templates()

        self.stdout.write(self.style.SUCCESS(f"✅ Template generated successfully!"))

    def generate_form_template(self):
        """Generate a form template using Django template rendering."""
        template_path = os.path.join(self.templates_dir, f"{self.name}_form.html")

        if os.path.exists(template_path) and not self.force:
            raise CommandError(f"Template already exists: {template_path}")

        model_fields = self.fields if self.fields else ["name", "description"]

        # Context for template rendering
        context = {
            "name": self.name,
            "model_name": self.model_name or "Item",
            "fields": [field.strip() for field in model_fields if field.strip()],
        }

        # Render template using Django template engine
        template_content = render_to_string(
            "django_tabler_theme/management/form.html", context
        )

        with open(template_path, "w") as f:
            f.write(template_content)

        self.stdout.write(f"Created form template: {template_path}")

    def generate_table_template(self):
        """Generate a table template using Django template rendering."""
        template_path = os.path.join(self.templates_dir, f"{self.name}_table.html")

        if os.path.exists(template_path) and not self.force:
            raise CommandError(f"Template already exists: {template_path}")

        model_fields = self.fields if self.fields else ["name", "created_at", "status"]

        # Context for template rendering
        context = {
            "name": self.name,
            "model_name": self.model_name or "Items",
            "model_name_singular": (self.model_name or "item").lower(),
            "fields": [field.strip() for field in model_fields if field.strip()],
        }

        # Render template using Django template engine
        template_content = render_to_string(
            "django_tabler_theme/management/table.html", context
        )

        with open(template_path, "w") as f:
            f.write(template_content)

        self.stdout.write(f"Created table template: {template_path}")

    def generate_dashboard_template(self):
        """Generate a dashboard template using Django template rendering."""
        template_path = os.path.join(self.templates_dir, f"{self.name}_dashboard.html")

        if os.path.exists(template_path) and not self.force:
            raise CommandError(f"Template already exists: {template_path}")

        # Context for template rendering
        context = {"name": self.name}

        # Render template using Django template engine
        template_content = render_to_string(
            "django_tabler_theme/management/dashboard.html", context
        )

        with open(template_path, "w") as f:
            f.write(template_content)

        self.stdout.write(f"Created dashboard template: {template_path}")

    def generate_page_template(self):
        """Generate a basic page template using Django template rendering."""
        template_path = os.path.join(self.templates_dir, f"{self.name}.html")

        if os.path.exists(template_path) and not self.force:
            raise CommandError(f"Template already exists: {template_path}")

        # Context for template rendering
        context = {"name": self.name, "title": self.name.title()}

        # Render template using Django template engine
        template_content = render_to_string(
            "django_tabler_theme/management/page.html", context
        )

        with open(template_path, "w") as f:
            f.write(template_content)

        self.stdout.write(f"Created page template: {template_path}")

    def generate_auth_templates(self):
        """Generate authentication templates using Django template rendering."""
        auth_templates = ["login.html"]  # We can add more later

        for template_name in auth_templates:
            template_path = os.path.join(self.templates_dir, template_name)

            if os.path.exists(template_path) and not self.force:
                self.stdout.write(f"Skipping existing template: {template_path}")
                continue

            # Context for template rendering
            context = {
                "template_name": template_name.replace(".html", ""),
                "brand_name": "Your Brand",
                "use_cdn": True,
                "logo_url": None,
            }

            # Render template using Django template engine
            template_content = render_to_string(
                "django_tabler_theme/management/login.html", context
            )

            with open(template_path, "w") as f:
                f.write(template_content)

            self.stdout.write(f"Created auth template: {template_path}")
