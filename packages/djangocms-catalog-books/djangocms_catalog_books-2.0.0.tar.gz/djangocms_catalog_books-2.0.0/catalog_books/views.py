import re
from typing import Any, Callable

from aldryn_apphooks_config.managers.base import AppHookConfigQuerySet
from aldryn_apphooks_config.mixins import AppConfigMixin
from cms.utils.page import get_page_from_request
from django.db.models import Q
from django.http import Http404, HttpRequest
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from .cms_appconfig import CatalogBooksConfig
from .constants import AUDIO_BOOKS, BOOKS_LIST_ORDER, EBOOK_FORMATS, BookType, ListType, OrderType, ParamType
from .models import Book, StorePage

ParamsDict = dict[str, Any]


def _set_param_int(params: ParamsDict, request: HttpRequest, param_type: str) -> None:
    """Set parameter int into parameters."""
    try:
        values = set(map(int, request.GET.getlist(param_type)))
        if values:
            params[param_type] = values
    except ValueError:
        pass


def _set_param(params: ParamsDict, request: HttpRequest, param_type: str, normalizer: Callable) -> None:
    """Set parameter into parameters."""
    values = set(map(normalizer, request.GET.getlist(param_type)))
    if values:
        params[param_type] = values


def get_page_list_params(request: HttpRequest) -> ParamsDict:
    """Get Books list page parameters."""
    params: ParamsDict = {}
    _set_param_int(params, request, ParamType.categories.value)
    _set_param_int(params, request, ParamType.authors.value)
    _set_param_int(params, request, ParamType.issue_years.value)
    _set_param_int(params, request, ParamType.licenses.value)
    _set_param(params, request, ParamType.book_formats.value, lambda n: re.sub("[^A-Za-z34]", "", n)[:4])
    _set_param(params, request, ParamType.book_types.value, lambda n: re.sub("[^A-Za-z0-9]", "", n)[:5])
    return params


class BookMixin:
    """Book mixin."""

    default_list_type = ListType.tiles.value

    config: CatalogBooksConfig
    kwargs: dict[str, str]
    request: HttpRequest

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        if self.config is None:
            width, height = 0, 0
            group_by, css_code = '', ''
        else:
            if self.kwargs.get('list_type', self.default_list_type) == ListType.tiles.value:
                width, height = self.config.tiles_thumbnail_width, self.config.tiles_thumbnail_height
                group_by = self.config.tiles_group_by
                css_code = self.config.tiles_css
            else:
                width, height = self.config.list_thumbnail_width, self.config.list_thumbnail_height
                group_by = self.config.list_group_by
                css_code = self.config.list_css
        order_codes = dict(BOOKS_LIST_ORDER)
        order_by = self.kwargs.get('order', OrderType.issue_desc.value)
        kwargs.update({
            'current_page': get_page_from_request(self.request),
            'is_catalog_config': self.config is not None,
            'thumbnail_width': width,
            'thumbnail_height': height,
            'thumbnail_size': f'{width}x{height}',
            'group_by_items': group_by,
            'books_css_name': css_code,
            'books_list_type': self.kwargs.get('list_type', self.default_list_type),
            'books_list_order': self.kwargs.get('order', OrderType.issue_desc.value),
            'BOOKS_LIST_ORDER': order_codes,
            'current_order_by': order_by,
            'page_params': get_page_list_params(self.request),
        })
        return super().get_context_data(**kwargs)  # type: ignore [misc]


class BookListView(BookMixin, AppConfigMixin, ListView):
    """Book list view."""

    model = Book

    def _get_book_types(self, params: ParamsDict) -> Q:
        """Get params for book types."""
        where = Q()
        for btype in params.get(ParamType.book_types.value, []):
            try:
                book_type = BookType(btype)
            except ValueError:
                continue
            if book_type is BookType.ebook:
                for ext in EBOOK_FORMATS.keys():
                    where |= Q(ebooks__original_filename__iendswith=f'.{ext}')
            if book_type is BookType.audio:
                for ext in AUDIO_BOOKS.keys():
                    where |= Q(ebooks__original_filename__iendswith=f'.{ext}')
            if book_type is BookType.paper:
                where |= Q(pk__in=StorePage.objects.values_list('store_pages', flat=True).all())
        return where

    def get_where(self) -> Q:
        """Get where part for queryset."""
        where = Q()
        params = get_page_list_params(self.request)
        if params.get(ParamType.categories.value):
            where &= Q(category__in=params.get(ParamType.categories.value))
        if params.get(ParamType.authors.value):
            where &= Q(authors__in=params.get(ParamType.authors.value))
        if params.get(ParamType.issue_years.value):
            where &= Q(issue__year__in=params.get(ParamType.issue_years.value))
        if params.get(ParamType.licenses.value):
            where &= Q(license__in=params.get(ParamType.licenses.value))
        if params.get(ParamType.book_formats.value):
            where_ext = Q()
            for ext in params.get(ParamType.book_formats.value, []):
                where_ext |= Q(ebooks__original_filename__iendswith=f'.{ext}')
            where &= where_ext
        if params.get(ParamType.book_types.value):
            where &= self._get_book_types(params)
        return where

    def get_queryset(self) -> AppHookConfigQuerySet:
        queryset: AppHookConfigQuerySet = super().get_queryset()
        if not (self.request.toolbar and self.request.toolbar.edit_mode_active):
            queryset = queryset.exclude(hide=True)
        order_by = self.kwargs.get('order', OrderType.issue_desc.value)
        return queryset.namespace(self.namespace).filter(self.get_where()).order_by(order_by).distinct()

    def get_paginate_by(self, queryset: AppHookConfigQuerySet) -> int:
        try:
            if self.kwargs.get('list_type', self.default_list_type) == ListType.tiles.value:
                return self.config.tiles_paginate_by
            else:
                return self.config.list_paginate_by
        except AttributeError:
            return 10

    def get_template_names(self):
        code = self.kwargs.get('list_type', self.default_list_type)
        return [f'catalog_books/book_{code}.html']


class BookDetailView(BookMixin, AppConfigMixin, DetailView):
    model = Book
    template_name = 'catalog_books/book_detail.html'

    def _get_context_by_pk(self, request: HttpRequest) -> dict[str, Any]:
        self.object = self.get_object()
        if self.object.hide and not (request.toolbar and request.toolbar.edit_mode_active):
            raise Http404()
        return self.get_context_data_detail(object=self.object)

    def _get_context_by_book_nmae(self, kwargs: dict[str, str]) -> dict[str, Any]:
        self.object = None
        queryset = self.get_queryset()
        if not (self.request.toolbar and self.request.toolbar.edit_mode_active):
            queryset = queryset.exclude(hide=True)
        queryset = queryset.filter(name=kwargs["name"])
        if queryset.count() > 1:
            context = self.get_context_data(book_list=queryset)
        elif queryset.count() == 1:
            self.object = queryset.first()
            context = self.get_context_data_detail(object=self.object)
        else:
            raise Http404()
        return context

    def get(self, request, *args, **kwargs):
        context = self._get_context_by_book_nmae(kwargs) if "name" in kwargs else self._get_context_by_pk(request)
        return self.render_to_response(context)

    def get_context_data_detail(self, **kwargs):
        width, height = self.config.detail_thumbnail_width, self.config.detail_thumbnail_height
        width_50perc, height_50perc = int(round(width * 0.5)), int(round(height * 0.5))
        kwargs.update({
            'thumbnail_width': width,
            'thumbnail_height': height,
            'thumbnail_size': f'{width}x{height}',
            'thumbnail_width_50perc': width_50perc,
            'thumbnail_height_50perc': height_50perc,
            'thumbnail_size_50perc': f'{width_50perc}x{height_50perc}',
            'books_css_name': self.config.detail_css,
        })
        return super().get_context_data(**kwargs)

    def get_template_names(self):
        if self.object is None:
            code = self.kwargs.get('list_type', self.default_list_type)
            return [f'catalog_books/book_{code}.html']
        return super().get_template_names()
