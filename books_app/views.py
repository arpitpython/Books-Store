from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from .models import Book
from .utils import get_list_param
from .serializers import BookSerializer
from .pagination import CustomPagination


class BookListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BookSerializer
    pagination_class = CustomPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gutenberg_id']
    search_fields = [
            'title', 'authors__name', 'subjects__name', 'bookshelves__name', 'languages__code', 'formats__mime_type'
        ]
    ordering_fields = ['download_count', 'title']
    ordering = ['-download_count']  

    def get_queryset(self):
        queryset = Book.objects.prefetch_related(
            'authors', 'subjects', 'bookshelves', 'languages', 'formats'
        ).only(
            'id', 'title', 'gutenberg_id', 'media_type', 'download_count'
        )

        topic = get_list_param(self.request, 'topic')
        author = get_list_param(self.request, 'author')
        title = get_list_param(self.request, 'title')
        language = get_list_param(self.request, 'language')
        mime_type = get_list_param(self.request, 'mime_type')
        
        if topic:
            topic_filter = Q()
            for word in topic:
                topic_filter |= Q(subjects__name__icontains=word) | Q(bookshelves__name__icontains=word)
            queryset = queryset.filter(topic_filter)

        if author:
            author_filter = Q()
            for a in author:
                author_filter |= Q(authors__name__icontains=a)
            queryset = queryset.filter(author_filter)

        if title:
            title_filter = Q()
            for t in title:
                title_filter |= Q(title__icontains=t)
            queryset = queryset.filter(title_filter)

        if language:
            queryset = queryset.filter(languages__code__in=language)

        if mime_type:
            queryset = queryset.filter(formats__mime_type__in=mime_type)

        return queryset.distinct()
