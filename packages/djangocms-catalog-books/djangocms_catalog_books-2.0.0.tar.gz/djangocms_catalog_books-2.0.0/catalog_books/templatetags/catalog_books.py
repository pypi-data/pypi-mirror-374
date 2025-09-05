import pathlib
from typing import Optional

from cms.templatetags.cms_tags import MultiValueArgument, Placeholder, PlaceholderOptions
from django import template
from django.conf import settings
from django.db.models.query import QuerySet
from django.template.context import RequestContext
from django.utils.http import urlencode
from filer.models.filemodels import File

from catalog_books.constants import ALL_BOOK_FORMATS
from catalog_books.models import Book

register = template.Library()


@register.filter(is_safe=True)
def file_extension(instance: File) -> str:
    """Display file extension."""
    return pathlib.Path(instance.original_filename).suffix[1:]


@register.filter(is_safe=True)
def file_ext_description(instance: File) -> str:
    """Display file extension."""
    extension = pathlib.Path(instance.original_filename).suffix[1:]
    return ALL_BOOK_FORMATS.get(extension, extension.upper())


@register.filter()
def books_list_page_params(page_params: dict, page: Optional[int] = None) -> str:
    params = []
    page_set = False
    for key, value in page_params.items():
        if key == 'page' and page is not None:
            value = page
            page_set = True
        if isinstance(value, (list, set, tuple)):
            for item in value:
                params.append((key, item))
        else:
            params.append((key, value))
    if page is not None and not page_set:
        params.append(('page', page))
    return "?" + urlencode(params) if params else ""


@register.filter()
def camel_case(text: str) -> str:
    """Convert string to camel case format, but first letter keep lower case."""
    chunks = text.split('-')
    if len(chunks) > 1:
        return "".join([chunks[0]] + [chunk.capitalize() for chunk in chunks[1:]])
    return text


@register.filter()
def map_language_code(text: str, language_code: str) -> str:
    """Replace text LANGUAGE_CODE by language_code value."""
    return text.replace('LANGUAGE_CODE', language_code)


def get_show_hidden(context: RequestContext) -> bool:
    """Get show hidden book."""
    request = context['request']
    return request.toolbar and request.toolbar.edit_mode_active


@register.simple_tag(takes_context=True)
def have_authors_more_books(context: RequestContext, book: Book) -> bool:
    """Check if the authors have written more books."""
    return book.have_authors_more_books(get_show_hidden(context))


@register.simple_tag(takes_context=True)
def get_authors_more_books(context: RequestContext, book: Book) -> QuerySet:
    """Get more books."""
    return book.get_authors_more_books(get_show_hidden(context))


class CatalogBooksPlaceholder(Placeholder):
    """Placeholder tag with defined name."""

    options = PlaceholderOptions(
        MultiValueArgument('extra_bits', required=False, resolve=False),
        blocks=[
            ('endplaceholder', 'nodelist'),
        ],
    )

    def render_tag(self, context, extra_bits, nodelist=None):
        try:
            name = settings.CATALOG_BOOKS_PLACEHOLDER_NAME
        except AttributeError:
            name = "content"  # Default placeholder name.
        return super().render_tag(context, name, extra_bits, nodelist)


register.tag('placeholder_catalog_book_page_content', CatalogBooksPlaceholder)
