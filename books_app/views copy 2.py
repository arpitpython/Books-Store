from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Case, When
from django_elasticsearch_dsl.search import Search
from elasticsearch_dsl import A

from .models import Book
from .utils import get_list_param
from .serializers import BookSerializer
from .pagination import CustomPagination
from .documents import BookDocument


def book_search_query(request, search_query):
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', CustomPagination.page_size))
    start = (page - 1) * page_size
    end = page * page_size

    # Base query for reuse
    base_search = BookDocument.search().query(
        "multi_match",
        query=search_query,
        fields=[
            "title^3", "authors", "subjects", "bookshelves", "languages", "formats"
        ],
        fuzziness="1"
    ).extra(collapse={"field": "id"})

    count_search = base_search[:0]
    count_search.aggs.metric('distinct_books', A('cardinality', field='id'))
    count_result = count_search.execute()
    length = count_result.aggregations.distinct_books.value

    # ✅ Run paginated query
    results = base_search[start:end].execute()
    matched_ids = [int(hit.meta.id) for hit in results]

    # ✅ Prepare ordered queryset for DRF
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(matched_ids)])
    queryset = Book.objects.filter(id__in=matched_ids).prefetch_related(
        'authors', 'subjects', 'bookshelves', 'languages', 'formats'
    ).order_by(preserved)

    return queryset, length



class BookListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BookSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['gutenberg_id']
    ordering_fields = ['download_count', 'title']
    ordering = ['-download_count']

    def get_queryset(self):
        search_query = self.request.query_params.get('search', '').strip()
        if search_query:
            queryset, length = book_search_query(self.request, search_query)
            self._es_count = length
            
            # preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(matched_ids)])
            # queryset = Book.objects.filter(id__in=matched_ids).prefetch_related(
            #     'authors', 'subjects', 'bookshelves', 'languages', 'formats'
            # ).order_by(preserved)
        else:
            queryset = Book.objects.prefetch_related(
                'authors', 'subjects', 'bookshelves', 'languages', 'formats'
            )
            self._es_count = None

        topic = get_list_param(self.request, 'topic')
        if topic:
            topic_q = Q()
            for word in topic:
                word = word.strip()
                topic_q |= Q(subjects__name__icontains=word)
                topic_q |= Q(bookshelves__name__icontains=word)
            queryset = queryset.filter(topic_q)

        author = get_list_param(self.request, 'author')
        if author:
            q = Q()
            for a in author:
                q |= Q(authors__name__icontains=a)
            queryset = queryset.filter(q)

        title = get_list_param(self.request, 'title')
        if title:
            q = Q()
            for t in title:
                q |= Q(title__icontains=t)
            queryset = queryset.filter(q)

        language = get_list_param(self.request, 'language')
        if language:
            queryset = queryset.filter(languages__code__in=language)

        mime_type = get_list_param(self.request, 'mime_type')
        if mime_type:
            queryset = queryset.filter(formats__mime_type__in=mime_type)

        return queryset
