from django.urls import path, register_converter

from .url_converters import BooksOrderByConverter, ListTypeConverter
from .views import BookDetailView, BookListView

register_converter(BooksOrderByConverter, 'order')
register_converter(ListTypeConverter, 'lstype')

urlpatterns = [
    # Note: The default url for the application must remain empty path ''.
    path('', BookListView.as_view(), name='book_list'),
    path('books-<lstype:list_type>/<order:order>/', BookListView.as_view(), name='book_list_order'),
    path('detail/<int:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('detail/<str:name>/', BookDetailView.as_view(), name='book_detail_by_name'),
]
