from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps
import os
import shutil


class Command(BaseCommand):
    help = "Copy django-tabler-theme templates to your project for customization"

    def add_arguments(self, parser):
        parser.add_argument(
            "template",
            nargs="?",
            help='Specific template to copy (e.g., "base.html")',
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Copy all available templates",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List available templates",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing files",
        )
        parser.add_argument(
            "--output-dir",
            type=str,
            default="templates/tabler_theme",
            help="Output directory (default: templates/tabler_theme)",
        )

    def handle(self, *args, **options):
        self.template_name = options.get("template")
        self.copy_all = options.get("all", False)
        self.list_templates = options.get("list", False)
        self.force = options.get("force", False)
        self.output_dir = options.get("output_dir")

        if self.list_templates:
            self.list_available_templates()
            return

        self.stdout.write(
            self.style.SUCCESS("📋 Django Tabler Theme Template Copy Tool")
        )
        self.stdout.write("")

        # Get the source template directory
        try:
            import django_tabler_theme

            source_dir = os.path.join(
                os.path.dirname(django_tabler_theme.__file__),
                "templates",
                "tabler_theme",
            )
        except ImportError:
            raise CommandError("django-tabler-theme not found")

        if not os.path.exists(source_dir):
            raise CommandError(f"Source template directory not found: {source_dir}")

        # Set up output directory
        output_path = os.path.join(settings.BASE_DIR, self.output_dir)
        os.makedirs(output_path, exist_ok=True)

        if self.copy_all:
            self.copy_all_templates(source_dir, output_path)
        elif self.template_name:
            self.copy_single_template(source_dir, output_path, self.template_name)
        else:
            self.stdout.write(
                self.style.ERROR(
                    "Please specify a template name or use --all or --list"
                )
            )
            self.stdout.write("Use --help for more information")

    def list_available_templates(self):
        """List all available templates."""
        self.stdout.write("📄 Available Templates:")
        self.stdout.write("")

        try:
            import django_tabler_theme

            source_dir = os.path.join(
                os.path.dirname(django_tabler_theme.__file__),
                "templates",
                "tabler_theme",
            )
        except ImportError:
            self.stdout.write(self.style.ERROR("django-tabler-theme not found"))
            return

        if not os.path.exists(source_dir):
            self.stdout.write(
                self.style.ERROR(f"Template directory not found: {source_dir}")
            )
            return

        templates = []
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".html"):
                    rel_path = os.path.relpath(os.path.join(root, file), source_dir)
                    templates.append(rel_path)

        if templates:
            for template in sorted(templates):
                self.stdout.write(f"  • {template}")
        else:
            self.stdout.write("  No templates found")

        self.stdout.write("")
        self.stdout.write("💡 Usage examples:")
        self.stdout.write("  python manage.py tabler_copy base.html")
        self.stdout.write("  python manage.py tabler_copy --all")
        self.stdout.write("  python manage.py tabler_copy --list")

    def copy_single_template(self, source_dir, output_path, template_name):
        """Copy a single template file."""
        source_file = os.path.join(source_dir, template_name)
        output_file = os.path.join(output_path, template_name)

        if not os.path.exists(source_file):
            raise CommandError(f"Template not found: {template_name}")

        # Create subdirectories if needed
        output_subdir = os.path.dirname(output_file)
        if output_subdir and output_subdir != output_path:
            os.makedirs(output_subdir, exist_ok=True)

        if os.path.exists(output_file) and not self.force:
            raise CommandError(
                f"Template already exists: {output_file}\n" "Use --force to overwrite"
            )

        try:
            shutil.copy2(source_file, output_file)
            self.stdout.write(
                self.style.SUCCESS(f"✅ Copied: {template_name} → {output_file}")
            )

            # Show customization instructions
            self.show_customization_tips(template_name, output_file)

        except Exception as e:
            raise CommandError(f"Failed to copy template: {e}")

    def copy_all_templates(self, source_dir, output_path):
        """Copy all template files."""
        copied_count = 0
        skipped_count = 0

        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".html"):
                    source_file = os.path.join(root, file)
                    rel_path = os.path.relpath(source_file, source_dir)
                    output_file = os.path.join(output_path, rel_path)

                    # Create subdirectories if needed
                    output_subdir = os.path.dirname(output_file)
                    if output_subdir and output_subdir != output_path:
                        os.makedirs(output_subdir, exist_ok=True)

                    if os.path.exists(output_file) and not self.force:
                        self.stdout.write(f"⏭️  Skipped (exists): {rel_path}")
                        skipped_count += 1
                        continue

                    try:
                        shutil.copy2(source_file, output_file)
                        self.stdout.write(self.style.SUCCESS(f"✅ Copied: {rel_path}"))
                        copied_count += 1
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"❌ Failed to copy {rel_path}: {e}")
                        )

        self.stdout.write("")
        self.stdout.write(f"📊 Summary: {copied_count} copied, {skipped_count} skipped")

        if copied_count > 0:
            self.show_general_customization_tips(output_path)

    def show_customization_tips(self, template_name, output_file):
        """Show template-specific customization tips."""
        self.stdout.write("")
        self.stdout.write("💡 Customization Tips:")

        if template_name == "base.html":
            self.stdout.write("  • This is the main layout template")
            self.stdout.write(
                "  • Customize navigation, header, footer, and overall structure"
            )
            self.stdout.write(
                "  • Add custom CSS/JS in the head_extra and scripts_extra blocks"
            )
            self.stdout.write("  • Modify the navigation menu in the navbar section")

        elif "form" in template_name.lower():
            self.stdout.write("  • Customize form styling and layout")
            self.stdout.write("  • Add custom form validation and error handling")
            self.stdout.write("  • Modify form field rendering")

        elif "auth" in template_name.lower() or "login" in template_name.lower():
            self.stdout.write("  • Customize authentication forms and pages")
            self.stdout.write("  • Add branding and custom styling")
            self.stdout.write("  • Modify redirect URLs and form behavior")

        else:
            self.stdout.write("  • Customize styling, layout, and content")
            self.stdout.write("  • Add custom blocks and template logic")

        self.stdout.write(f"  • Template location: {output_file}")
        self.stdout.write("")

    def show_general_customization_tips(self, output_path):
        """Show general customization tips after copying all templates."""
        self.stdout.write("")
        self.stdout.write("💡 Next Steps:")
        self.stdout.write("")
        self.stdout.write("1. Template Priority:")
        self.stdout.write(f"   Django will now use templates from {output_path}")
        self.stdout.write("   instead of the default django-tabler-theme templates.")
        self.stdout.write("")
        self.stdout.write("2. Safe Customization:")
        self.stdout.write("   • Make incremental changes and test frequently")
        self.stdout.write("   • Keep backups of working versions")
        self.stdout.write("   • Use version control to track changes")
        self.stdout.write("")
        self.stdout.write("3. Common Customizations:")
        self.stdout.write("   • base.html: Overall layout, navigation, branding")
        self.stdout.write("   • CSS/JS: Add custom styling and behavior")
        self.stdout.write("   • Forms: Customize form rendering and validation")
        self.stdout.write("")
        self.stdout.write("4. Template Inheritance:")
        self.stdout.write(
            "   • Your templates can still extend django-tabler-theme templates"
        )
        self.stdout.write(
            '   • Use {% extends "tabler_theme/base.html" %} for partial customization'
        )
        self.stdout.write("")
        self.stdout.write("5. Updates:")
        self.stdout.write("   • When updating django-tabler-theme, review changes")
        self.stdout.write("   • Compare your customized templates with new versions")
        self.stdout.write(
            "   • Run: python manage.py tabler_copy --list to see available templates"
        )
        self.stdout.write("")

        # Check if TEMPLATES configuration needs updating
        self.check_template_dirs_config(output_path)

    def check_template_dirs_config(self, output_path):
        """Check if TEMPLATES DIRS includes the output directory."""
        template_dirs = []
        for template_config in settings.TEMPLATES:
            template_dirs.extend(template_config.get("DIRS", []))

        # Check if our output directory or its parent is in DIRS
        base_templates_dir = os.path.join(settings.BASE_DIR, "templates")

        if (
            base_templates_dir in template_dirs
            or str(settings.BASE_DIR) in template_dirs
        ):
            self.stdout.write("✅ Template directory configuration looks good")
        else:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("⚠️  Template Directory Configuration"))
            self.stdout.write(
                "Add the following to your TEMPLATES DIRS in settings.py:"
            )
            self.stdout.write("")
            self.stdout.write("TEMPLATES = [")
            self.stdout.write("    {")
            self.stdout.write(
                "        'BACKEND': 'django.template.backends.django.DjangoTemplates',"
            )
            self.stdout.write("        'DIRS': [")
            self.stdout.write(f"            BASE_DIR / 'templates',  # Add this line")
            self.stdout.write("        ],")
            self.stdout.write("        # ... rest of configuration")
            self.stdout.write("    },")
            self.stdout.write("]")
            self.stdout.write("")
