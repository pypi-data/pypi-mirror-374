# django-tabler-theme

A reusable Django theme app using Tabler (Bootstrap 5) with templates, components, and helpers.

## Features

- Django templates based on Tabler UI kit
- Bootstrap 5 integration
- Reusable components and template tags
- Easy integration with Django projects

## Installation

```bash
pip install django-tabler-theme
```

## Quick Start

1. Add `tabler_theme` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'tabler_theme',
    ...
]
```

2. Include the theme's context processor in your `TEMPLATES` setting:

```python
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'django_tabler_theme.context_processors.tabler_theme',
                ...
            ],
        },
    },
]
```

## Development

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies: `pip install -e .[dev]`
4. Run tests: `pytest`

## License

MIT License
