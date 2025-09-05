from .constants import ListType, OrderType


class BooksOrderByConverter:
    """Order by Converter."""

    regex = f'({OrderType.name.value}|{OrderType.name_desc.value}|{OrderType.issue.value}|{OrderType.issue_desc.value})'

    def to_python(self, value: str) -> OrderType:
        """Convert url to param."""
        return OrderType(value)

    def to_url(self, order: OrderType) -> str:
        """Convert params to url."""
        return order.value


class ListTypeConverter:
    """List type Converter."""

    regex = f'({ListType.list.value}|{ListType.tiles.value})'

    def to_python(self, value: str) -> ListType:
        """Convert url to param."""
        return ListType(value)

    def to_url(self, ltype: ListType) -> str:
        """Convert params to url."""
        return ltype.value
