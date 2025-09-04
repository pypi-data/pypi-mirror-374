from django import template
from django.template.loader import get_template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag('django_pagination_widget/pagination.html', takes_context=True)
def pagination_widget(context, page_obj, page_range=None):
    """
    Renders the pagination widget with smart ellipsis logic.

    Usage:
        {% load pagination_tags %}
        {% pagination_widget page_obj %}

    Args:
        page_obj: Django's Page object from Paginator
        page_range: Optional list of page numbers to display
    """
    if page_range is None:
        # Smart pagination range with ellipsis to avoid FOUC
        page_range = get_smart_page_range(page_obj)

    return {
        'page_obj': page_obj,
        'page_range': page_range,
        'request': context.get('request'),
    }


def get_smart_page_range(page_obj):
    """
    Generate smart page range with ellipsis to avoid FOUC.
    Only renders necessary buttons, not all pages.
    """
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages

    # For small number of pages, show all
    if total_pages <= 7:
        return list(range(1, total_pages + 1))

    # Always show first page
    pages = [1]

    # Calculate range around current page
    start = max(2, current_page - 1)
    end = min(total_pages - 1, current_page + 1)

    # Add ellipsis after first page if needed
    if start > 2:
        pages.append('...')

    # Add pages around current page
    for page in range(start, end + 1):
        if page not in pages:
            pages.append(page)

    # Add ellipsis before last page if needed
    if end < total_pages - 1:
        pages.append('...')

    # Always show last page
    if total_pages > 1 and total_pages not in pages:
        pages.append(total_pages)

    return pages


@register.simple_tag
def pagination_css():
    """
    Returns the CSS link tag for pagination styling.

    Usage:
        {% load pagination_tags %}
        {% pagination_css %}
    """
    href = static('django_pagination_widget/css/pagination.css')
    return mark_safe(f'<link rel="stylesheet" href="{href}">')


@register.simple_tag
def pagination_js():
    """
    Returns the JavaScript script tag for pagination behavior.

    Usage:
        {% load pagination_tags %}
        {% pagination_js %}
    """
    src = static('django_pagination_widget/js/pagination.js')
    return mark_safe(f'<script src="{src}"></script>')


@register.simple_tag
def pagination_custom_css(custom_css_path=None):
    """
    Returns a CSS link tag for custom pagination styling.

    Usage:
        {% load pagination_tags %}
        {% pagination_custom_css 'my_app/css/custom-pagination.css' %}

    Args:
        custom_css_path: Path to custom CSS file relative to static root
    """
    if custom_css_path:
        href = static(custom_css_path)
        return mark_safe(f'<link rel="stylesheet" href="{href}">')
    return ''
