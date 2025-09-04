from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.apps import apps
import os
import textwrap


class Command(BaseCommand):
    help = "Set up django-tabler-theme in your Django project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--app",
            type=str,
            help="Specify the app name for template creation",
        )
        parser.add_argument(
            "--templates-dir",
            type=str,
            default="templates",
            help="Templates directory (default: templates)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing files",
        )
        parser.add_argument(
            "--check-only",
            action="store_true",
            help="Only check configuration, do not create files",
        )

    def handle(self, *args, **options):
        self.app_name = options.get("app")
        self.templates_dir = options.get("templates_dir")
        self.force = options.get("force")
        self.check_only = options.get("check_only")

        self.stdout.write(self.style.SUCCESS("🚀 Django Tabler Theme Setup Wizard"))
        self.stdout.write("")

        # Check current configuration
        self.check_configuration()

        if self.check_only:
            return

        # Create templates directory
        self.create_templates_directory()

        # Create base template
        self.create_base_template()

        # Create sample templates if app is specified
        if self.app_name:
            self.create_app_templates()

        # Show next steps
        self.show_next_steps()

    def check_configuration(self):
        """Check current django-tabler-theme configuration."""
        self.stdout.write(self.style.WARNING("📋 Checking Configuration..."))

        # Check if app is installed
        if "django_tabler_theme" in settings.INSTALLED_APPS:
            self.stdout.write("✅ django_tabler_theme is in INSTALLED_APPS")
        else:
            self.stdout.write(
                self.style.ERROR("❌ django_tabler_theme not in INSTALLED_APPS")
            )

        # Check context processor
        context_processors = []
        for template_config in settings.TEMPLATES:
            if "context_processors" in template_config.get("OPTIONS", {}):
                context_processors.extend(
                    template_config["OPTIONS"]["context_processors"]
                )

        if (
            "django_tabler_theme.context_processors.tabler_settings"
            in context_processors
        ):
            self.stdout.write("✅ Context processor is configured")
        else:
            self.stdout.write(self.style.ERROR("❌ Context processor not configured"))

        # Check TABLER_THEME setting
        if hasattr(settings, "TABLER_THEME"):
            self.stdout.write("✅ TABLER_THEME configuration found")
            theme_config = getattr(settings, "TABLER_THEME")
            if theme_config.get("BRAND_NAME"):
                self.stdout.write(f'   Brand: {theme_config["BRAND_NAME"]}')
            if theme_config.get("LOGO_URL"):
                self.stdout.write(f'   Logo: {theme_config["LOGO_URL"]}')
        else:
            self.stdout.write(
                self.style.WARNING("⚠️  TABLER_THEME not configured (using defaults)")
            )

        self.stdout.write("")

    def create_templates_directory(self):
        """Create templates directory if it doesn't exist."""
        templates_path = os.path.join(settings.BASE_DIR, self.templates_dir)

        if not os.path.exists(templates_path):
            os.makedirs(templates_path)
            self.stdout.write(
                self.style.SUCCESS(f"✅ Created templates directory: {templates_path}")
            )
        else:
            self.stdout.write(f"📁 Templates directory exists: {templates_path}")

    def create_base_template(self):
        """Create a base template extending tabler_theme."""
        base_template_path = os.path.join(
            settings.BASE_DIR, self.templates_dir, "base.html"
        )

        if os.path.exists(base_template_path) and not self.force:
            self.stdout.write(f"📄 Base template exists: {base_template_path}")
            return

        base_template_content = textwrap.dedent(
            """
            {% extends "tabler_theme/base.html" %}
            {% load static %}

            {% block title %}{% if page_title %}{{ page_title }} - {% endif %}{{ block.super }}{% endblock %}

            {% block topnav_items %}
              <li class="nav-item">
                <a class="nav-link" href="{% url 'home' %}">
                  <span class="nav-link-title">Home</span>
                </a>
              </li>
              {# Add more navigation items here #}
            {% endblock %}

            {% block topnav_right_title %}
              {% if user.is_authenticated %}
                {{ user.get_full_name|default:user.username }}
              {% else %}
                Guest
              {% endif %}
            {% endblock %}

            {% block topnav_right_subtitle %}
              {% if user.is_authenticated %}
                {{ user.email }}
              {% else %}
                Not logged in
              {% endif %}
            {% endblock %}

            {% block topnav_right_items %}
              {% if user.is_authenticated %}
                <a class="dropdown-item" href="{% url 'admin:index' %}">
                  <i class="ti ti-settings me-2"></i>
                  Admin
                </a>
                <div class="dropdown-divider"></div>
                <a class="dropdown-item" href="{% url 'logout' %}">
                  <i class="ti ti-logout me-2"></i>
                  Logout
                </a>
              {% else %}
                <a class="dropdown-item" href="{% url 'login' %}">
                  <i class="ti ti-login me-2"></i>
                  Login
                </a>
              {% endif %}
            {% endblock %}

            {% block page_title %}
              {% if page_title %}
                <div class="page-header d-print-none">
                  <div class="container-xl">
                    <div class="row g-2 align-items-center">
                      <div class="col">
                        <h1 class="page-title">{{ page_title }}</h1>
                        {% if page_description %}
                          <div class="text-secondary mt-1">{{ page_description }}</div>
                        {% endif %}
                      </div>
                    </div>
                  </div>
                </div>
              {% endif %}
            {% endblock %}

            {% block head_extra %}
              {# Add custom CSS/JS here #}
            {% endblock %}

            {% block scripts_extra %}
              {# Add custom scripts here #}
            {% endblock %}
        """
        ).strip()

        with open(base_template_path, "w") as f:
            f.write(base_template_content)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Created base template: {base_template_path}")
        )

    def create_app_templates(self):
        """Create sample templates for the specified app."""
        if not self.app_name:
            return

        # Check if app exists
        try:
            apps.get_app_config(self.app_name)
        except LookupError:
            self.stdout.write(self.style.ERROR(f'❌ App "{self.app_name}" not found'))
            return

        app_templates_dir = os.path.join(
            settings.BASE_DIR, self.templates_dir, self.app_name
        )
        os.makedirs(app_templates_dir, exist_ok=True)

        # Create home template
        self.create_home_template(app_templates_dir)

        # Create list template
        self.create_list_template(app_templates_dir)

        # Create detail template
        self.create_detail_template(app_templates_dir)

    def create_home_template(self, app_templates_dir):
        """Create a home page template."""
        home_template_path = os.path.join(app_templates_dir, "home.html")

        if os.path.exists(home_template_path) and not self.force:
            return

        home_template_content = textwrap.dedent(
            """
            {% extends "base.html" %}

            {% block content %}
            <div class="container-xl">
              <div class="row row-deck row-cards">
                <div class="col-12">
                  <div class="card">
                    <div class="card-header">
                      <h3 class="card-title">Welcome to Your App</h3>
                    </div>
                    <div class="card-body">
                      <p>This is your Django application with Tabler theme!</p>
                      <div class="btn-list">
                        <a href="#" class="btn btn-primary">Get Started</a>
                        <a href="#" class="btn btn-outline-primary">Learn More</a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            {% endblock %}
        """
        ).strip()

        with open(home_template_path, "w") as f:
            f.write(home_template_content)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Created home template: {home_template_path}")
        )

    def create_list_template(self, app_templates_dir):
        """Create a list view template."""
        list_template_path = os.path.join(app_templates_dir, "list.html")

        if os.path.exists(list_template_path) and not self.force:
            return

        list_template_content = textwrap.dedent(
            """
            {% extends "base.html" %}

            {% block content %}
            <div class="container-xl">
              <div class="row row-cards">
                {% for item in object_list %}
                  <div class="col-sm-6 col-lg-4">
                    <div class="card card-sm">
                      <div class="card-body">
                        <div class="row align-items-center">
                          <div class="col-auto">
                            <span class="bg-primary text-white avatar">{{ item.name|first|upper }}</span>
                          </div>
                          <div class="col">
                            <div class="font-weight-medium">
                              <a href="#" class="text-reset">{{ item.name }}</a>
                            </div>
                            <div class="text-secondary">
                              {{ item.description|truncatewords:10 }}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                {% empty %}
                  <div class="col-12">
                    <div class="empty">
                      <div class="empty-img">
                        <img src="https://cdn.jsdelivr.net/npm/@tabler/core@latest/dist/img/undraw_printing_invoices_5r4r.svg" height="128" alt="">
                      </div>
                      <p class="empty-title">No items found</p>
                      <p class="empty-subtitle text-secondary">
                        Try adjusting your search or filter to find what you're looking for.
                      </p>
                    </div>
                  </div>
                {% endfor %}
              </div>
              
              {% if is_paginated %}
                <div class="d-flex mt-4">
                  <ul class="pagination ms-auto">
                    {% if page_obj.has_previous %}
                      <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.previous_page_number }}">
                          <i class="ti ti-chevron-left"></i>
                          prev
                        </a>
                      </li>
                    {% endif %}
                    
                    {% for num in page_obj.paginator.page_range %}
                      {% if page_obj.number == num %}
                        <li class="page-item active">
                          <a class="page-link" href="#">{{ num }}</a>
                        </li>
                      {% elif num > page_obj.number|add:'-3' and num < page_obj.number|add:'3' %}
                        <li class="page-item">
                          <a class="page-link" href="?page={{ num }}">{{ num }}</a>
                        </li>
                      {% endif %}
                    {% endfor %}
                    
                    {% if page_obj.has_next %}
                      <li class="page-item">
                        <a class="page-link" href="?page={{ page_obj.next_page_number }}">
                          next
                          <i class="ti ti-chevron-right"></i>
                        </a>
                      </li>
                    {% endif %}
                  </ul>
                </div>
              {% endif %}
            </div>
            {% endblock %}
        """
        ).strip()

        with open(list_template_path, "w") as f:
            f.write(list_template_content)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Created list template: {list_template_path}")
        )

    def create_detail_template(self, app_templates_dir):
        """Create a detail view template."""
        detail_template_path = os.path.join(app_templates_dir, "detail.html")

        if os.path.exists(detail_template_path) and not self.force:
            return

        detail_template_content = textwrap.dedent(
            """
            {% extends "base.html" %}

            {% block content %}
            <div class="container-xl">
              <div class="row">
                <div class="col-lg-8">
                  <div class="card">
                    <div class="card-header">
                      <h3 class="card-title">{{ object.name }}</h3>
                    </div>
                    <div class="card-body">
                      <div class="markdown">
                        {{ object.description|linebreaks }}
                      </div>
                    </div>
                    <div class="card-footer">
                      <div class="btn-list">
                        <a href="#" class="btn btn-primary">
                          <i class="ti ti-pencil me-1"></i>
                          Edit
                        </a>
                        <a href="#" class="btn btn-outline-primary">
                          <i class="ti ti-arrow-left me-1"></i>
                          Back to list
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col-lg-4">
                  <div class="card">
                    <div class="card-header">
                      <h3 class="card-title">Details</h3>
                    </div>
                    <div class="card-body">
                      <div class="datagrid">
                        <div class="datagrid-item">
                          <div class="datagrid-title">Created</div>
                          <div class="datagrid-content">{{ object.created_at|date:"M d, Y" }}</div>
                        </div>
                        {% if object.updated_at %}
                          <div class="datagrid-item">
                            <div class="datagrid-title">Updated</div>
                            <div class="datagrid-content">{{ object.updated_at|date:"M d, Y" }}</div>
                          </div>
                        {% endif %}
                        {% if object.author %}
                          <div class="datagrid-item">
                            <div class="datagrid-title">Author</div>
                            <div class="datagrid-content">{{ object.author.get_full_name|default:object.author.username }}</div>
                          </div>
                        {% endif %}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            {% endblock %}
        """
        ).strip()

        with open(detail_template_path, "w") as f:
            f.write(detail_template_content)

        self.stdout.write(
            self.style.SUCCESS(f"✅ Created detail template: {detail_template_path}")
        )

    def show_next_steps(self):
        """Show next steps to the user."""
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("🎉 Setup Complete!"))
        self.stdout.write("")
        self.stdout.write("📝 Next steps:")
        self.stdout.write("")

        if "django_tabler_theme" not in settings.INSTALLED_APPS:
            self.stdout.write(
                "1. Add django_tabler_theme to INSTALLED_APPS in settings.py:"
            )
            self.stdout.write("   INSTALLED_APPS = [..., 'django_tabler_theme']")
            self.stdout.write("")

        context_processors = []
        for template_config in settings.TEMPLATES:
            if "context_processors" in template_config.get("OPTIONS", {}):
                context_processors.extend(
                    template_config["OPTIONS"]["context_processors"]
                )

        if (
            "django_tabler_theme.context_processors.tabler_settings"
            not in context_processors
        ):
            self.stdout.write("2. Add context processor to TEMPLATES in settings.py:")
            self.stdout.write(
                "   'django_tabler_theme.context_processors.tabler_settings'"
            )
            self.stdout.write("")

        if not hasattr(settings, "TABLER_THEME"):
            self.stdout.write("3. Add TABLER_THEME configuration to settings.py:")
            self.stdout.write("   TABLER_THEME = {")
            self.stdout.write("       'BRAND_NAME': 'Your App Name',")
            self.stdout.write("       'USE_CDN': True,")
            self.stdout.write("   }")
            self.stdout.write("")

        self.stdout.write("4. Create views and URLs for your templates")
        self.stdout.write("5. Run: python manage.py runserver")
        self.stdout.write("")
        self.stdout.write("💡 Use these commands for more help:")
        self.stdout.write("   python manage.py tabler_generate --help")
        self.stdout.write("   python manage.py tabler_check")
        self.stdout.write("")
