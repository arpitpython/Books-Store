from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=128, db_index=True) 
    birth_year = models.SmallIntegerField(null=True, blank=True)
    death_year = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'books_author'


class Subject(models.Model):
    name = models.CharField(max_length=256, db_index=True) 

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'books_subject'


class Bookshelf(models.Model):
    name = models.CharField(max_length=64, db_index=True) 

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'books_bookshelf'


class Language(models.Model):
    code = models.CharField(max_length=4, db_index=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'books_language'


class Book(models.Model):
    title = models.CharField(max_length=1024, db_index=True)
    gutenberg_id = models.IntegerField(unique=True, db_index=True)
    media_type = models.CharField(max_length=16, db_index=True)  
    download_count = models.IntegerField(default=0, db_index=True) 

    authors = models.ManyToManyField(Author, through='BookAuthor', related_name='books')
    subjects = models.ManyToManyField(Subject, through='BookSubject', related_name='books')
    bookshelves = models.ManyToManyField(Bookshelf, through='BookBookshelf', related_name='books')
    languages = models.ManyToManyField(Language, through='BookLanguage', related_name='books')

    def __str__(self):
        return self.title
    
    @property
    def authors_indexing(self):
        return [author.name for author in self.authors.all()]

    @property
    def subjects_indexing(self):
        return [sub.name for sub in self.subjects.all()]

    @property
    def bookshelves_indexing(self):
        return [shelf.name for shelf in self.bookshelves.all()]

    @property
    def languages_indexing(self):
        return [lang.code for lang in self.languages.all()]

    @property
    def formats_indexing(self):
        return [f.mime_type for f in self.formats.all()]

    class Meta:
        db_table = 'books_book'


class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_authors', db_index=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_books', db_index=True)

    class Meta:
        unique_together = ('book', 'author')
        db_table = 'books_book_authors'


class BookSubject(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_subjects', db_index=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='subject_books', db_index=True)

    class Meta:
        unique_together = ('book', 'subject')
        db_table = 'books_book_subjects'


class BookBookshelf(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_bookshelves', db_index=True)
    bookshelf = models.ForeignKey(Bookshelf, on_delete=models.CASCADE, related_name='bookshelf_books', db_index=True)

    class Meta:
        unique_together = ('book', 'bookshelf')
        db_table = 'books_book_bookshelves'


class BookLanguage(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_languages', db_index=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, related_name='language_books', db_index=True)

    class Meta:
        unique_together = ('book', 'language')
        db_table = 'books_book_languages'


class Format(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='formats', db_index=True)
    mime_type = models.CharField(max_length=32, db_index=True) 
    url = models.URLField(max_length=256)

    def __str__(self):
        return f'{self.mime_type} ({self.book.title})'

    class Meta:
        db_table = 'books_format'

