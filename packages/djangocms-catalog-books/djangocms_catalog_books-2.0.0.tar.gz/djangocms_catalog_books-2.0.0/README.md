# Catalog of Books

The program is designed to manage eBooks for free download. However, it is also possible to link to bookstore sales pages.

The program is built on the  [Django CMS](https://www.django-cms.org/) framework. Many different items can be set in the book administration. From the book title and author's name, to ISBN, license, preview and sample book.

The program itself does not contain any cascading styles or javascript code. `CSS` styles and `js` are in the example attached to the program. See the following screenshots.

#### List as tiles

![Catalog tiles](https://gitlab.nic.cz/djangocms-apps/djangocms-catalog-books/-/raw/main/snapshosts/catalog-tiles.png "Catalog tiles")

#### List of books

![Catalog list](https://gitlab.nic.cz/djangocms-apps/djangocms-catalog-books/-/raw/main/snapshosts/catalog-list.png "Catalog list")

#### Detail of the book

![Book detail](https://gitlab.nic.cz/djangocms-apps/djangocms-catalog-books/-/raw/main/snapshosts/book-detail.png "Book detail")

#### Book editing

![Change book](https://gitlab.nic.cz/djangocms-apps/djangocms-catalog-books/-/raw/main/snapshosts/change-book.png "Change book")

#### List of books in the administration

![Edit books](https://gitlab.nic.cz/djangocms-apps/djangocms-catalog-books/-/raw/main/snapshosts/edit-books.png "Edit books")

## Install

Install the package from pypi.org.

```
pip install djangocms-catalog-books
```

Add into `INSTALLED_APPS` in your site `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'aldryn_apphooks_config',
    'catalog_books',
]
```

## Site example

Along with the program, an example is stored in the repository that you can run in the docker.

Download the example:

```
curl https://gitlab.nic.cz/djangocms-apps/djangocms-catalog-books/-/archive/main/djangocms-catalog-books-main.zip?path=example --output example.zip
```

Extract the archive and go to the folder:

```
unzip example.zip
cd djangocms-catalog-books-main-example/example/
```

Build the image:

```
docker build -t books .
```

Run the site:

```
docker run --rm -d -p 8000:8000 --name books_example books
```

Open the site in your browser: http://localhost:8000/. You'll see what's in the screenshots.

Login to the administration: http://localhost:8000/admin with username `admin` and password `password`.

Stop the site:

```
docker stop books_example
```


## License

GPLv3+
