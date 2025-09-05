from django.test import SimpleTestCase

from catalog_books.models import Author, Book, Category, License


class AuthorTest(SimpleTestCase):

    def test_str(self):
        instance = Author(first_name="Tom", last_name="Tester")
        self.assertEqual(str(instance), "Tester Tom")

    def test_no_first_name(self):
        instance = Author(last_name="Tester")
        self.assertEqual(str(instance), "Tester")


class CategoryTest(SimpleTestCase):

    def test_str(self):
        instance = Category(name="Technical literature", slug="tech")
        self.assertEqual(str(instance), "Technical literature (tech)")


class LicenseTest(SimpleTestCase):

    def test_str(self):
        instance = License(name="BSD")
        self.assertEqual(str(instance), "BSD")

    def test_str_version(self):
        instance = License(name="CC", version="BY, SA")
        self.assertEqual(str(instance), "CC BY, SA")


class BookTest(SimpleTestCase):

    def test_str(self):
        instance = Book(name="It")
        self.assertEqual(str(instance), "It")
