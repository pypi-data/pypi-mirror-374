from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _

from .cms_appconfig import CatalogBooksConfig


@apphook_pool.register
class CatalogBooksApphook(CMSConfigApp):
    name = _("Catalog of Books")
    app_name = "catalog_books"
    app_config = CatalogBooksConfig

    def get_urls(self, page=None, language=None, **kwargs):
        return ["catalog_books.urls"]
