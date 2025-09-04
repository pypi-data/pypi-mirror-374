from django.apps import AppConfig


class DjangoPaginationWidgetConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_pagination_widget'
    verbose_name = 'Django Pagination Widget'

    def ready(self):
        """
        Initialize app settings and configurations.
        """
        pass
