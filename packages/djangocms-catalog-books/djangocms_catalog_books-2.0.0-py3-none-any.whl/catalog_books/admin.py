from aldryn_apphooks_config.admin import BaseAppHookConfig, ModelAppHookConfig
from cms.admin.placeholderadmin import FrontendEditableAdminMixin, PlaceholderAdminMixin
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .cms_appconfig import CatalogBooksConfig
from .forms import BookForm
from .models import Author, Book, Bookstore, Category, License, StorePage


class AuthorAdmin(admin.ModelAdmin):
    """Author Admin."""

    list_display = (
        'first_name',
        'last_name',
    )
    list_filter = (
        'last_name',
        'first_name',
    )
    list_display_links = ["first_name", "last_name"]


class CategoryAdmin(admin.ModelAdmin):
    """Category Admin."""

    list_display = (
        'name', 'slug',
    )
    list_filter = (
        'name', 'slug',
    )


class LicenseAdmin(admin.ModelAdmin):
    """License Admin."""

    list_display = (
        'name', 'version',
    )
    list_filter = (
        'name',
    )


class BookstoreAdmin(admin.ModelAdmin):
    """Bookstore Admin."""

    list_display = (
        'name',
    )
    list_filter = (
        'name',
    )


class StorePageAdmin(admin.ModelAdmin):
    """Store page Admin."""

    list_display = (
        'bookstore', 'view_books',
    )
    list_filter = (
        'bookstore',
    )

    @admin.display(empty_value="", description=_("Book"))
    def view_books(self, obj):
        return '"' + ", ".join(obj.store_pages.values_list('name', flat=True).all()) + '"'


class BookAdmin(PlaceholderAdminMixin, FrontendEditableAdminMixin, ModelAppHookConfig, admin.ModelAdmin):
    """Book Admin."""

    date_hierarchy = "issue"
    list_display = (
        'name',
        'hide',
        'view_authors',
        'issue',
    )
    list_filter = (
        'name',
    )
    form = BookForm
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "description",
                    "new",
                    "bestseller",
                    "coming_soon",
                    "hide",
                    "issue",
                    "isbn",
                    "bibliographic_description",
                    "dimensions",
                    "authors",
                    "authors_and_team",
                    "category",
                    "license",
                    "preview",
                    "sample",
                    "ebooks",
                    "stores",
                ],
            },
        ),
        (
            _("Advanced options"),
            {
                "classes": ["collapse"],
                "fields": ["app_config"],
            },
        ),
    ]

    @admin.display(empty_value="", description=_("Authors"))
    def view_authors(self, obj):
        authors_and_team = " " + _("and team") if obj.authors_and_team else ""
        return ", ".join(map(str, obj.authors.all())) + authors_and_team


class CatalogConfigAdmin(PlaceholderAdminMixin, BaseAppHookConfig, admin.ModelAdmin):

    def get_config_fields(self):
        return (
            'title',
            'list_group_by', 'tiles_group_by',
            'list_paginate_by', 'tiles_paginate_by',
            'list_css', 'tiles_css', 'detail_css',
            "list_thumbnail_width", "list_thumbnail_height",
            "tiles_thumbnail_width", "tiles_thumbnail_height",
            "detail_thumbnail_width", "detail_thumbnail_height",
        )


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(Bookstore, BookstoreAdmin)
admin.site.register(StorePage, StorePageAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(CatalogBooksConfig, CatalogConfigAdmin)
