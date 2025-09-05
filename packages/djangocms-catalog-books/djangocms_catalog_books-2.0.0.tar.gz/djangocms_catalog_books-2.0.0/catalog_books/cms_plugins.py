import pathlib
from typing import Any, NamedTuple

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from cms.plugin_rendering import PluginContext
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .constants import ALL_BOOK_FORMATS, BookType, ParamType
from .models import Author, Book, ButtonSubmit, Category, License
from .views import get_page_list_params


class NameCount(NamedTuple):
    name: str
    value: Any
    slug: str
    number: int
    checked: bool = False


class PluginMixin:
    """Plugin mixin for include common context."""

    input_name = ''
    class_suffix = ''
    title = ''
    books_filter_checked = 'books_filter_checked'
    cache = False

    def _is_public(self, request: HttpRequest) -> bool:
        return not (request.toolbar and request.toolbar.edit_mode_active)

    def _get_book_queryset(self, request: HttpRequest) -> QuerySet:
        queryset = Book.objects.all()
        if self._is_public(request):
            queryset = queryset.exclude(hide=True)
        return queryset

    def render(self, context: PluginContext, instance: CMSPlugin, placeholder: str) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)  # type: ignore[misc]
        context['input_name'] = self.input_name
        context['class_suffix'] = self.class_suffix
        context['title'] = self.title
        if self.books_filter_checked not in context:
            params = get_page_list_params(context['request'])
            context[self.books_filter_checked] = params.get(self.input_name, [])
        return context


@plugin_pool.register_plugin
class BookTypesPlugin(PluginMixin, CMSPluginBase):
    module = _('Catalog of Books')
    name = _('Book types')
    render_template = "catalog_books/plugin.html"
    input_name = ParamType.book_types.value
    class_suffix = 'types'
    title = _('Type')

    def render(self, context: PluginContext, instance: CMSPlugin, placeholder: str) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        # context['object_list'] is filtered queryset <AppHookConfigQuerySet [<Book: Title>, ...].
        checked = context[self.books_filter_checked]
        book_types: dict[BookType, int] = {
            BookType.ebook: 0,
            BookType.audio: 0,
            BookType.paper: 0,
        }
        for book in self._get_book_queryset(context['request']):
            book.populate_book_types(book_types)
        sorted_types = []
        if book_types[BookType.ebook]:
            sorted_types.append(NameCount(
                _("E-Book"), BookType.ebook.value, BookType.ebook.value, book_types[BookType.ebook],
                BookType.ebook.value in checked))
        if book_types[BookType.audio]:
            sorted_types.append(NameCount(
                _("Audiobook"), BookType.audio.value, BookType.audio.value, book_types[BookType.audio],
                BookType.audio.value in checked))
        if book_types[BookType.paper]:
            sorted_types.append(NameCount(
                _("Book"), BookType.paper.value, BookType.paper.value, book_types[BookType.paper],
                BookType.paper.value in checked))
        context['object_list'] = sorted_types
        return context


@plugin_pool.register_plugin
class AuthorsPlugin(PluginMixin, CMSPluginBase):
    module = _('Catalog of Books')
    name = _('Book authors')
    render_template = "catalog_books/plugin.html"
    input_name = ParamType.authors.value
    class_suffix = 'authors'
    title = _('Author')

    def render(self, context: PluginContext, instance: CMSPlugin, placeholder: str) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        checked = context[self.books_filter_checked]
        object_list = []
        for author in Author.objects.all().order_by('last_name', 'first_name'):
            if self._is_public(context['request']):
                books_num = author.book_set.filter(hide=False).count()
            else:
                books_num = author.book_set.count()
            if books_num:
                slug = f'{author.last_name} {author.first_name}'
                object_list.append(NameCount(author, author.pk, slug, books_num, author.pk in checked))
        context['object_list'] = object_list
        return context


@plugin_pool.register_plugin
class CategoriesPlugin(PluginMixin, CMSPluginBase):
    module = _('Catalog of Books')
    name = _('Book categories')
    render_template = "catalog_books/plugin.html"
    input_name = ParamType.categories.value
    class_suffix = 'categories'
    title = _('Categories')

    def render(self, context: PluginContext, instance: CMSPlugin, placeholder: str) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        checked = context[self.books_filter_checked]
        categories: dict[Category, int] = {}
        for book in self._get_book_queryset(context['request']):
            for category in book.category.all():
                if category in categories:
                    categories[category] += 1
                else:
                    categories[category] = 1
        sorted_types = []
        for category in Category.objects.all().order_by('name'):
            if category in categories:
                sorted_types.append(NameCount(category.name, category.pk, category.slug, categories[category],
                                              category.pk in checked))
        context['object_list'] = sorted_types
        return context


@plugin_pool.register_plugin
class IssueYearsPlugin(PluginMixin, CMSPluginBase):
    module = _('Catalog of Books')
    name = _('Book issue years')
    render_template = "catalog_books/plugin.html"
    input_name = ParamType.issue_years.value
    class_suffix = 'issue-years'
    title = _('Issue year')

    def render(self, context: PluginContext, instance: CMSPlugin, placeholder: str) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        checked = context[self.books_filter_checked]
        object_dict: dict[int, int] = {}
        for book in self._get_book_queryset(context['request']):
            if book.issue.year in object_dict:
                object_dict[book.issue.year] += 1
            else:
                object_dict[book.issue.year] = 1
        object_list = []
        for item in sorted(object_dict.items(), key=lambda item: item[0], reverse=True):
            object_list.append(NameCount(str(item[0]), item[0], str(item[0]), item[1], item[0] in checked))
        context['object_list'] = object_list
        return context


@plugin_pool.register_plugin
class LicensesPlugin(PluginMixin, CMSPluginBase):
    module = _('Catalog of Books')
    name = _('Book licenses')
    render_template = "catalog_books/plugin.html"
    input_name = ParamType.licenses.value
    class_suffix = 'licenses'
    title = _('Licenses')

    def render(self, context: PluginContext, instance: CMSPlugin, placeholder: str) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        checked = context[self.books_filter_checked]
        object_list = []
        for license in License.objects.all().order_by('name', 'version'):
            if self._is_public(context['request']):
                books_num = license.book_set.filter(hide=False).count()
            else:
                books_num = license.book_set.count()
            if books_num:
                object_list.append(NameCount(license, license.pk, str(license), books_num, license.pk in checked))
        context['object_list'] = object_list
        return context


@plugin_pool.register_plugin
class BookFormatsPlugin(PluginMixin, CMSPluginBase):
    module = _('Catalog of Books')
    name = _('Book formats')
    render_template = "catalog_books/plugin.html"
    input_name = ParamType.book_formats.value
    class_suffix = 'formats'
    title = _('Formats')

    def render(self, context: PluginContext, instance: CMSPlugin, placeholder: str) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        checked = context[self.books_filter_checked]
        book_types: dict[str, int] = {}
        for book in self._get_book_queryset(context['request']):
            for book_file in book.ebooks.all():
                ext = pathlib.Path(book_file.original_filename).suffix[1:].lower()
                if ext in book_types:
                    book_types[ext] += 1
                else:
                    book_types[ext] = 1
        sorted_types = []
        for ext in ALL_BOOK_FORMATS.keys():
            if ext in book_types:
                sorted_types.append(NameCount(ext, ext, ext, book_types[ext], ext in checked))
        context['object_list'] = sorted_types
        return context


@plugin_pool.register_plugin
class ButtonSubmitPlugin(CMSPluginBase):
    module = _('Catalog of Books')
    model = ButtonSubmit
    name = _('Submit button')
    render_template = "catalog_books/button.html"
