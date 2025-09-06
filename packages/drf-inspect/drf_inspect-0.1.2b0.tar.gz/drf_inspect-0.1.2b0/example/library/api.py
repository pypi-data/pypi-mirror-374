from django.db.models import Count
from library.models import Author, Book
from library.serializers import AuthorSerializer, BookSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from drf_inspect.build import build_serializer_graph


class AuthorModelViewSet(viewsets.ModelViewSet):
    serializer_class = AuthorSerializer
    queryset = Author.objects.annotate(book_count=Count('books'))

    graph = build_serializer_graph(serializer_class)
    print(f'{graph!r}')

    @action(
        methods=['get'],
        detail=True,
        serializer_class=BookSerializer,
    )
    def books(self, request: Request, *args, **kwargs):
        author = self.get_object()
        serializer = self.get_serializer(author.books.all(), many=True)

        return Response(serializer.data)


class BookModelViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
