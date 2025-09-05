from django import forms
from django.db.models import Case, Q, When
from django.utils.html import format_html_join
from django.utils.translation import gettext_lazy as _

from .constants import ALL_BOOK_FORMATS
from .models import Book


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        exclude: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        where = Q()
        for name in ALL_BOOK_FORMATS.keys():
            where |= Q(original_filename__iendswith=f".{name}")
        self.fields['ebooks'].queryset = self.fields['ebooks'].queryset.filter(where)
        self.fields['ebooks'].help_text += (
            " " + _("Only formats are allowed:") + " <span class='available-ebook-formats'>" +
            format_html_join(", ", "<span title='{1}'>{0}</span>", ALL_BOOK_FORMATS.items()) + "</span>.")
        self.fields['authors'].queryset = self.fields['authors'].queryset.order_by('last_name', 'first_name')
        self.fields['category'].queryset = self.fields['category'].queryset.order_by('name')
        self.fields['license'].queryset = self.fields['license'].queryset.order_by('name', 'version')
        self.fields['stores'].queryset = self.fields['stores'].queryset.order_by('store_pages__name')
        samples = sorted([(str(item).lower(), item.pk) for item in self.fields['sample'].queryset.all()])
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate([item[1] for item in samples])])
        self.fields['sample'].queryset = self.fields['sample'].queryset.order_by(preserved)
