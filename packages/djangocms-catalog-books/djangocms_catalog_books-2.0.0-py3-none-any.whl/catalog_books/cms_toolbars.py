from aldryn_apphooks_config.utils import get_app_instance
from aldryn_translation_tools.utils import get_admin_url, get_object_from_request
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.utils.translation import get_language_from_request
from django.utils.translation import gettext as _
from django.utils.translation import override

from .cms_appconfig import CatalogBooksConfig
from .models import Book


@toolbar_pool.register
class CatalogBooksToolbar(CMSToolbar):
    # watch_models must be a list, not a tuple
    # see https://github.com/divio/django-cms/issues/4135
    watch_models = [Book]
    supported_apps = ('catalog_books',)

    def get_on_delete_redirect_url(self, book, language):
        with override(language):
            url = reverse(
                f'{book.app_config.namespace}:book_list')
        return url

    def __get_catalogbooks_config(self):
        try:
            __, config = get_app_instance(self.request)
            if not isinstance(config, CatalogBooksConfig):
                # This is not the app_hook you are looking for.
                return None
        except ImproperlyConfigured:
            # There is no app_hook at all.
            return None

        return config

    def _populate_menu(self, config, user, view_name):
        """Populate menu for user."""
        language = get_language_from_request(self.request, check_path=True)

        # If we're on an Book detail page, then get the book
        if view_name == f'{config.namespace}:book_detail':
            book = get_object_from_request(Book, self.request)
        else:
            book = None

        menu = self.toolbar.get_or_create_menu('catalogbooks-app', config.get_app_title())

        change_config_perm = user.has_perm('catalog_books.change_catalogbooksconfig')
        add_config_perm = user.has_perm('catalog_books.add_catalogbooksconfig')
        config_perms = [change_config_perm, add_config_perm]

        change_book_perm = user.has_perm('catalog_books.change_book')
        delete_book_perm = user.has_perm('catalog_books.delete_book')
        add_book_perm = user.has_perm('catalog_books.add_book')
        book_perms = [change_book_perm, add_book_perm, delete_book_perm]

        if change_config_perm:
            url_args = {}
            if language:
                url_args = {'language': language}
            url = get_admin_url('catalog_books_catalogbooksconfig_change', [config.pk], **url_args)
            menu.add_modal_item(_('Configure addon'), url=url)

        if any(config_perms) and any(book_perms):
            menu.add_break()

        if change_book_perm:
            url_args = {}
            if config:
                url_args = {'app_config__id__exact': config.pk}
            url = get_admin_url('catalog_books_book_changelist', **url_args)
            menu.add_sideframe_item(_('Book list'), url=url)

        if add_book_perm:
            url_args = {'app_config': config.pk, 'owner': user.pk}
            if language:
                url_args.update({'language': language})
            url = get_admin_url('catalog_books_book_add', **url_args)
            menu.add_modal_item(_('Add new Book'), url=url)

        if change_book_perm and book:
            url_args = {}
            if language:
                url_args = {'language': language}
            url = get_admin_url('catalog_books_book_change', [book.pk], **url_args)
            menu.add_modal_item(_('Edit this book'), url=url, active=True)

        if delete_book_perm and book:
            redirect_url = self.get_on_delete_redirect_url(book, language=language)
            url = get_admin_url('catalog_books_book_delete', [book.pk])
            menu.add_modal_item(_('Delete this book'), url=url, on_close=redirect_url)

    def populate(self):
        config = self.__get_catalogbooks_config()
        if not config:
            # Do nothing if there is no CatalogBooks app_config to work with
            return

        user = getattr(self.request, 'user', None)
        try:
            view_name = self.request.resolver_match.view_name
        except AttributeError:
            view_name = None

        if user and view_name:
            self._populate_menu(config, user, view_name)
