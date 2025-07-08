from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        self.es_count = getattr(view, '_es_count', None)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        count = self.es_count if self.es_count is not None else self.page.paginator.count
        return Response({
            'count': count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
    
    