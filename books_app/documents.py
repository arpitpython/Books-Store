from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import Book


book_index = Index('books')
book_index.settings(number_of_shards=1, number_of_replicas=0)


@registry.register_document
class BookDocument(Document):
    authors = fields.TextField(attr='authors_indexing')
    subjects = fields.TextField(attr='subjects_indexing')
    bookshelves = fields.TextField(attr='bookshelves_indexing')
    languages = fields.TextField(attr='languages_indexing')
    formats = fields.TextField(attr='formats_indexing')

    class Index:
        name = 'books'

    class Django:
        model = Book
        fields = ['id', 'title', 'gutenberg_id', 'media_type', 'download_count']
