import pytest
from django.template import Context, Template
from django.test.client import RequestFactory
from django.urls import path
from django.http import HttpResponse
from django.test import override_settings


def dummy_view(request):
    return HttpResponse("Test")


# Simple URL patterns for testing
urlpatterns = [
    path("", dummy_view, name="home"),
    path("about/", dummy_view, name="about"),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF="tests.test_templatetags")
def test_nav_active_templatetag():
    """Test the nav_active template tag correctly identifies active URLs."""
    rf = RequestFactory()
    request = rf.get("/")

    template = Template(
        """
        {% load tabler %}
        <li class="{% nav_active 'home' %}">Home</li>
        <li class="{% nav_active 'about' %}">About</li>
    """
    )

    rendered = template.render(Context({"request": request}))

    # Home should be active, about should not
    assert 'class="active"' in rendered
    # Only one should be active
    assert rendered.count('class="active"') == 1


@pytest.mark.django_db
def test_add_class_filter():
    """Test the add_class filter adds CSS classes to form fields."""
    from django import forms

    class TestForm(forms.Form):
        name = forms.CharField()

    form = TestForm()

    template = Template(
        """
        {% load tabler %}
        {{ form.name|add_class:"form-control" }}
    """
    )

    rendered = template.render(Context({"form": form}))

    assert 'class="form-control"' in rendered
