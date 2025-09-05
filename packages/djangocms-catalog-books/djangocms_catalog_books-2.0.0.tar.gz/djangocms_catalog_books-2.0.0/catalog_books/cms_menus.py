from cms.apphook_pool import apphook_pool
from cms.menu_bases import CMSAttachMenu
from django.urls import NoReverseMatch
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext_lazy as _
from menus.base import NavigationNode
from menus.menu_pool import menu_pool

from .models import Book


class CatalogBooksMenu(CMSAttachMenu):
    name = _('Catalog of Books Menu')

    def get_queryset(self, request):
        """Return base queryset with support for preview-mode."""
        queryset = Book.objects
        if not (request.toolbar and request.toolbar.edit_mode_active):
            if hasattr(queryset, 'published'):
                queryset = queryset.published()
        return queryset

    def get_nodes(self, request):
        nodes = []
        language = get_language_from_request(request, check_path=True)
        books = self.get_queryset(request)

        if hasattr(self, 'instance') and self.instance:
            app = apphook_pool.get_apphook(self.instance.application_urls)
            if app:
                try:
                    config = app.get_config(self.instance.application_namespace)
                    if config:
                        books = books.filter(app_config=config)
                except NotImplementedError:
                    pass  # Configurable AppHooks must implement this method

        try:
            for book in books:
                try:
                    url = book.get_absolute_url(language=language)
                except NoReverseMatch:
                    url = None

                if url:
                    node = NavigationNode(book.name, url, book.pk)
                    nodes.append(node)
        except TypeError:
            # TypeError: 'AppHookConfigManager' object is not iterable.
            # This occurs when the application is not present but the menu is.
            pass
        return nodes


menu_pool.register_menu(CatalogBooksMenu)
