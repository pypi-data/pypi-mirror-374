from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


def catalog_books_urls_need_reloading(sender, **kwargs) -> None:
    """Reload urls when Sestion is added or removed."""
    from cms.appresolver import clear_app_resolvers
    from django.urls import clear_url_caches
    clear_app_resolvers()
    clear_url_caches()


class CatalogBooks(AppConfig):
    name = 'catalog_books'
    verbose_name = _('Catalog of Books')

    def ready(self):
        from cms.signals import urls_need_reloading
        urls_need_reloading.connect(catalog_books_urls_need_reloading)
