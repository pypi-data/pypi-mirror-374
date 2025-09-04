import pytest
from django.template import Context, Template
from django.conf import settings

# Configure Django settings for testing
if not settings.configured:
    settings.configure(
        DEBUG=True,
        INSTALLED_APPS=[
            'django_pagination_widget',
        ],
        SECRET_KEY='test-secret-key',
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [],
                },
            },
        ],
        STATIC_URL='/static/',
    )

import django
django.setup()

from django_pagination_widget.templatetags.pagination_tags import pagination_widget


class MockPageObj:
    """Mock Page object for testing"""
    def __init__(self, number=1, has_previous=False, has_next=True,
                 previous_page_number=None, next_page_number=2,
                 num_pages=10, paginator=None):
        self.number = number
        self.has_previous = has_previous
        self.has_next = has_next
        self.previous_page_number = previous_page_number
        self.next_page_number = next_page_number
        self.paginator = MockPaginator(num_pages)


class MockPaginator:
    """Mock Paginator for testing"""
    def __init__(self, num_pages=10):
        self.num_pages = num_pages


def test_pagination_widget_tag():
    """Test the pagination_widget template tag"""
    page_obj = MockPageObj()
    context = Context({'page_obj': page_obj})

    # Test template rendering
    template = Template("{% load pagination_tags %}{% pagination_widget page_obj %}")
    rendered = template.render(context)

    # Check that pagination elements are present
    assert 'pagination' in rendered
    assert 'page-change-btn' in rendered
    assert 'Page 1 of 10' in rendered


def test_pagination_with_custom_range():
    """Test pagination with custom page range"""
    page_obj = MockPageObj(number=5)
    page_range = [3, 4, 5, 6, 7]
    context = Context({'page_obj': page_obj, 'page_range': page_range})

    template = Template("{% load pagination_tags %}{% pagination_widget page_obj page_range %}")
    rendered = template.render(context)

    # Check custom range is used
    for page_num in page_range:
        assert f'btn-{page_num}' in rendered


def test_pagination_navigation():
    """Test navigation buttons"""
    # Test first page (no previous)
    page_obj = MockPageObj(number=1, has_previous=False, has_next=True, next_page_number=2)
    context = Context({'page_obj': page_obj})
    template = Template("{% load pagination_tags %}{% pagination_widget page_obj %}")
    rendered = template.render(context)

    assert 'back-btn' not in rendered  # No previous button
    assert 'next-btn' in rendered     # Has next button

    # Test middle page
    page_obj = MockPageObj(number=5, has_previous=True, has_next=True,
                          previous_page_number=4, next_page_number=6)
    context = Context({'page_obj': page_obj})
    rendered = template.render(context)

    assert 'back-btn' in rendered   # Has previous button
    assert 'next-btn' in rendered   # Has next button

    # Test last page (no next)
    page_obj = MockPageObj(number=10, has_previous=True, has_next=False,
                          previous_page_number=9, next_page_number=None)
    context = Context({'page_obj': page_obj})
    rendered = template.render(context)

    assert 'back-btn' in rendered     # Has previous button
    assert 'next-btn' not in rendered  # No next button


def test_pagination_css_tag():
    """Test pagination_css template tag returns safe link tag"""
    template = Template("{% load pagination_tags %}{% pagination_css %}")
    rendered = template.render(Context())

    assert 'django_pagination_widget/css/pagination.css' in rendered
    assert '<link' in rendered  # Now marked safe


def test_pagination_js_tag():
    """Test pagination_js template tag returns safe script tag"""
    template = Template("{% load pagination_tags %}{% pagination_js %}")
    rendered = template.render(Context())

    assert 'django_pagination_widget/js/pagination.js' in rendered
    assert '<script' in rendered  # Now marked safe


def test_template_tags_import():
    """Test that template tags can be imported"""
    from django_pagination_widget.templatetags import pagination_tags
    assert hasattr(pagination_tags, 'pagination_widget')
    assert hasattr(pagination_tags, 'pagination_css')
    assert hasattr(pagination_tags, 'pagination_js')


def test_package_structure():
    """Test that package structure is correct"""
    import django_pagination_widget
    assert django_pagination_widget.__version__ == "0.1.0"
    assert django_pagination_widget.__author__ is not None
