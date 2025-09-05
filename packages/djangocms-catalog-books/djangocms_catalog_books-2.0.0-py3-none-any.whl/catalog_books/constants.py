from enum import Enum, unique

from django.utils.translation import gettext_lazy as _

EBOOK_FORMATS = {
    'epub': _('EPUB (.epub) - An open eBook standard created by the International Digital Publishing Forum (IDPF). '
              'It features reflowable text, inline images and the ability to use Digital Rights Management (DRM) '
              'such as Adobe Digital Editions.'),
    'mobi': _('MobiPocket (.mobi) - A format primarily designed for PDAs and older mobile devices. '
              'Also used on the Kindle.'),
    'pdf': _('PDF (.pdf) - A very popular eBook format from Adobe which most eReaders support.'),
    'azw': _("Kindle (.azw) - Native format for Amazon's Kindle products which typically comes with DRM protection "
             "to limit sharing."),
    'azw3': _("Kindle (.azw3) - Native format for Amazon's Kindle products which typically comes with DRM protection "
              "to limit sharing."),
    'pdb': _('PalmDatabase (.pdb)'),
    'prc': _('MobiPocket (.prc)'),
    'lrf': _('LRF (.lrf) is an eBook reader file associated with Sony. It can contain text and images. '
             "It uses the DRM protection to ensure Sony's digital right. LRF files turn the data into binary file. "
             'LRF had been used for the eBooks of Sony eBook store before it was discontinued in 2010.'),
    'oeb': _('OEB (.oeb) is an XML based eBook file format. It is an open eBook Standard that can make order '
             'of the multiple sources and make the multiple sources into a single file. This file is DRM protected so '
             'the digital copyright of this book is available with this format. '
             'This format is used n online eBook stores.'),
    'docx': _('Text Office Open XML (.docx)'),
    'txt': _('Text (.txt) - A basic plain text format which is easy to create, but cannot contain images.'),
}

AUDIO_BOOKS = {
    'mp3': _('An MP3 file is the most common lossy audio format, and though the quality is slightly diminished, '
             'vocals still come through without much loss.'),
    'aax': _('AAX was an audiobook format developed by Audible using an MPEG-4 container that also allowed '
             'for the file to be encrypted with DRM.'),
    'm4a': _('The compressed format used by Apple, just as the AAX is used by Audible, is the M4A or M4B.'),
    'm4b': _('The compressed format used by Apple, just as the AAX is used by Audible, is the M4A or M4B.'),
    'aac': _("The AAC format stands for Advanced Audio Coding, and it's actually a superior form of compression when "
             "compared to the MP3."),
    'm4p': _('M4Ps are merely a version of AAC that have digital rights management included. It was originally built '
             'by Apple for the iTunes Music store.'),
    'ogg': _("OGG is a sort of digital container that holds Vorbis files. Vorbis files are open source. "
             "It's also a superior form of audio quality and compression."),
    'wma': _('WMA stands for Windows Media Audio, and there are both Lossy and Lossless formats for it.'),
    'wav': _("WAV is one of the most popular files types for audio. It's an older format, but despite this, "
             "it is still widely used."),
    'flac': _('FLAC is largely considered to be the most superior form of lossless compressed audio.'),
    'alac': _("Apple Lossless Audio Codec (ALAC) is Apple's own file format for high-quality audio."),
}

ALL_BOOK_FORMATS = {}
ALL_BOOK_FORMATS.update(EBOOK_FORMATS)
ALL_BOOK_FORMATS.update(AUDIO_BOOKS)


@unique
class OrderType(Enum):
    name = 'name'
    name_desc = '-name'
    issue = 'issue'
    issue_desc = '-issue'


BOOKS_LIST_ORDER = (
    (OrderType.issue_desc.value, _('from newest')),
    (OrderType.issue.value, _('from oldest')),
    (OrderType.name.value, _('by name A-Z')),
    (OrderType.name_desc.value, _('by name Z-A')),
)


@unique
class ListType(Enum):
    list = 'list'
    tiles = 'tiles'


@unique
class ParamType(Enum):
    categories = 'c'
    authors = 'a'
    issue_years = 'y'
    licenses = 'l'
    book_formats = 'f'
    book_types = 't'


@unique
class BookType(Enum):
    ebook = 'ebook'
    audio = 'audio'
    paper = 'paper'
