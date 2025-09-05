import pathlib
from datetime import datetime

from aldryn_apphooks_config.fields import AppHookConfigField
from aldryn_apphooks_config.managers import AppHookConfigManager
from cms.models.pluginmodel import CMSPlugin
from cms.utils.i18n import get_current_language
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import override, pgettext, pgettext_lazy
from djangocms_text.fields import HTMLField
from filer.fields.image import FilerImageField
from filer.models import File

from .cms_appconfig import CatalogBooksConfig
from .constants import AUDIO_BOOKS, EBOOK_FORMATS, BookType


class Author(models.Model):
    first_name = models.CharField(_("First name"), max_length=255, null=True, blank=True)
    last_name = models.CharField(_("Last name"), max_length=255)

    objects = AppHookConfigManager()

    class Meta:
        unique_together = ["first_name", "last_name"]

    def __str__(self):
        if self.first_name is None:
            return self.last_name
        return f"{self.last_name} {self.first_name}"


class Category(models.Model):
    name = models.CharField(_("Name"), unique=True, max_length=255)
    slug = models.SlugField(_("Slug"), unique=True, max_length=255, help_text=_("Slug for css class."))

    objects = AppHookConfigManager()

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.name} ({self.slug})"


class License(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    version = models.CharField(_("Version"), null=True, blank=True, max_length=255)
    icon = FilerImageField(verbose_name=_('Icon'), null=True, blank=True, on_delete=models.SET_NULL)
    description = HTMLField(_("Description"), default="")

    objects = AppHookConfigManager()

    class Meta:
        unique_together = ["name", "version"]

    def __str__(self):
        if self.version is None:
            return self.name
        return f"{self.name} {self.version}"


class Bookstore(models.Model):
    name = models.CharField(_("Name"), unique=True, max_length=255, help_text=_("Bookstore name."))

    def __str__(self):
        return self.name


class StorePage(models.Model):
    bookstore = models.ForeignKey(Bookstore, verbose_name=_("Bookstore"), on_delete=models.CASCADE)
    url = models.URLField('URL', unique=True, help_text=_("URL to the page with book."))

    def __str__(self):
        books = ", ".join(self.store_pages.values_list('name', flat=True).all())
        on = pgettext('books_on_bookstore', 'on')
        return f'"{books}" {on} {self.bookstore}'


class Book(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    description = HTMLField(_("Description"), default="")
    new = models.BooleanField(pgettext_lazy("new-book", "New"), default=False)
    bestseller = models.BooleanField(_("Bestseller"), default=False)
    coming_soon = models.BooleanField(_("Coming soon"), default=False)
    hide = models.BooleanField(_("Hide"), default=False, help_text=_('Hide this entry.'))
    issue = models.DateField(_("Issue"), default=datetime.today)
    authors = models.ManyToManyField(Author, verbose_name=_("Authors"), blank=True)
    authors_and_team = models.BooleanField(_("and team"), default=False, help_text=_("Authors and collective"))
    category = models.ManyToManyField(Category, verbose_name=_("Category"), blank=True)
    license = models.ForeignKey(License, verbose_name=_("License"), null=True, blank=True, on_delete=models.SET_NULL)
    isbn = models.CharField("ISBN", max_length=255, blank=True, null=True, help_text=_("e.g. 978-80-88168-67-6"))
    bibliographic_description = models.CharField(
        _("Bibliographic description"), max_length=255, blank=True, null=True,
        help_text=_("e.g. 1× book, paperback, 454 pages, Czech"))
    dimensions = models.CharField(_("Dimensions"), max_length=255, blank=True, null=True,
                                  help_text=_("e.g. 175 × 250 mm"))
    preview = FilerImageField(verbose_name=_('Preview'), related_name='preview', null=True, blank=True,
                              on_delete=models.SET_NULL, help_text=_("e.g. Book cover."))
    sample = models.ForeignKey(File, verbose_name=_('Sample'), null=True, blank=True, on_delete=models.SET_NULL)
    ebooks = models.ManyToManyField(File, related_name='files', verbose_name=_("E-Books files"), blank=True,
                                    help_text=_("Book files in different formats."))
    stores = models.ManyToManyField(StorePage, related_name='store_pages', verbose_name=_("Bookstores"), blank=True,
                                    help_text=_("Page of the bookstore selling this book."))
    app_config = AppHookConfigField(CatalogBooksConfig)

    objects = AppHookConfigManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self, language=None):
        """Return the url for this Article in the selected permalink format."""
        if not language:
            language = get_current_language()
        if self.app_config and self.app_config.namespace:
            namespace = f'{self.app_config.namespace}:'
        else:
            namespace = ''
        with override(language):
            return reverse(f'{namespace}book_detail', kwargs={"pk": self.pk})

    def populate_book_types(self, book_types: dict[BookType, int]) -> None:
        """Populate book types."""
        for book_file in self.ebooks.all():
            ext = pathlib.Path(book_file.original_filename).suffix[1:].lower()
            if ext in EBOOK_FORMATS:
                book_types[BookType.ebook] += 1
            elif ext in AUDIO_BOOKS:
                book_types[BookType.audio] += 1
        if self.stores.count():
            book_types[BookType.paper] += 1

    def get_book_types(self) -> list[str]:
        """Get book types."""
        book_types: dict[BookType, int] = {
            BookType.ebook: 0,
            BookType.audio: 0,
            BookType.paper: 0,
        }
        self.populate_book_types(book_types)
        sorted_types = []
        if book_types[BookType.ebook]:
            sorted_types.append(BookType.ebook.value)
        if book_types[BookType.audio]:
            sorted_types.append(BookType.audio.value)
        if book_types[BookType.paper]:
            sorted_types.append(BookType.paper.value)
        return sorted_types

    @property
    def published(self):
        return not self.hide

    def have_authors_more_books(self, show_hidden: bool = False) -> bool:
        """Check if the authors have written more books."""
        # Note: Book.objects.distinct() only work on PostgreSQL.
        books_id = Book.objects.values_list('id', flat=True).filter(
            hide=show_hidden, authors__in=self.authors.all()).exclude(pk=self.pk)
        return bool(len(set(tuple(books_id))))

    def get_authors_more_books(self, show_hidden: bool = False) -> QuerySet:
        """Return authors more books."""
        # Note: Book.objects.distinct() only work on PostgreSQL.
        books_id = Book.objects.values_list('id', flat=True).filter(
            hide=show_hidden, authors__in=self.authors.all()).exclude(pk=self.pk)
        return Book.objects.filter(pk__in=books_id)


class ButtonSubmit(CMSPlugin):
    text = models.CharField(_("Text"), max_length=255, help_text=_("Button text."))
    css = models.CharField(_("Css names"), null=True, blank=True, max_length=255,
                           help_text=_("Class names separated by space."))
    title = models.CharField("Title", null=True, blank=True, max_length=255,
                             help_text=_("Button attribute title."))

    def __str__(self):
        return self.text
