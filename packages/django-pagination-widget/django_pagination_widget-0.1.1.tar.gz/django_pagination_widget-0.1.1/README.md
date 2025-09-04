# Django Pagination Widget

A modern, zero-dependency Django pagination component with clean styling, accessible markup, and a tiny vanilla-JS helper for smart ellipsis.

Supports: Django 4.2+ · Python 3.9+

## Install

```bash
pip install django-pagination-widget
```

## Quick start

1) Add the app

```python
INSTALLED_APPS = [
	# ...
	"django_pagination_widget",
]
```

2) In your template

```html
{% load pagination_tags %}

<!-- Basic usage (widget auto-includes its CSS/JS) -->
{% pagination_widget page_obj %}

<!-- Or load assets once (e.g., in base.html) and reuse the widget -->
{% pagination_css %}
{% pagination_js %}
{% pagination_widget page_obj %}
```

Optional: include your own theme overrides

```html
{% pagination_custom_css 'css/pagination_widget.css' %}
```

## Links

- Source: https://github.com/priyesh-04/django-pagination-widget
- Issues: https://github.com/priyesh-04/django-pagination-widget/issues

License: MIT
