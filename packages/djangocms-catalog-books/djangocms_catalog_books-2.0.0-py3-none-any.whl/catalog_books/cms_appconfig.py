from aldryn_apphooks_config.models import AppHookConfig
from aldryn_apphooks_config.utils import setup_config
from app_data import AppDataForm
from django.db import models
from django.utils.translation import gettext_lazy as _


class CatalogBooksConfig(AppHookConfig, models.Model):
    """Catalog of Books config."""

    title = models.CharField(_('Title'), max_length=255)
    list_group_by = models.PositiveIntegerField(
            _('List Group size'),
            default=5,
            help_text=_('Number of items for group "Load more".'),
        )
    tiles_group_by = models.PositiveIntegerField(
            _('Tiles Group size'),
            default=9,
            help_text=_('Number of items for group "Load more".'),
        )
    list_paginate_by = models.PositiveIntegerField(
            _('List Paginate size'),
            default=50,
            help_text=_('Total number of items on the page.')
        )
    tiles_paginate_by = models.PositiveIntegerField(
            _('Tiles Paginate size'),
            default=50,
            help_text=_('Total number of items on the page.')
        )
    list_thumbnail_width = models.PositiveIntegerField(_('List Thumbnail Width'), default=196)
    list_thumbnail_height = models.PositiveIntegerField(_('List Thumbnail Height'), default=261)

    tiles_thumbnail_width = models.PositiveIntegerField(_('Tiles Thumbnail Width'), default=306)
    tiles_thumbnail_height = models.PositiveIntegerField(_('Tiles Thumbnail Height'), default=408)

    detail_thumbnail_width = models.PositiveIntegerField(_('Detail Thumbnail Width'), default=319)
    detail_thumbnail_height = models.PositiveIntegerField(_('Detail Thumbnail Height'), default=453)

    list_css = models.SlugField(
        _('List CSS Class'), max_length=255, null=True, blank=True,
        help_text=_("Set extra css class. E.g. display-button-more."))
    tiles_css = models.SlugField(
        _('Tiles CSS Class'), max_length=255, null=True, blank=True,
        help_text=_("Set extra css class. E.g. display-button-more."))
    detail_css = models.SlugField(
        _('Detail CSS Class'), max_length=255, null=True, blank=True,
        help_text=_("Set extra css class."))

    class Meta:
        verbose_name = _('Configuration')
        verbose_name_plural = _('Configurations')

    def __str__(self):
        return self.title

    def get_app_title(self):
        return getattr(self, 'title', _('untitled'))


class CatalogBooksConfigForm(AppDataForm):
    """Catalog of Books Config Form."""


setup_config(CatalogBooksConfigForm, CatalogBooksConfig)
