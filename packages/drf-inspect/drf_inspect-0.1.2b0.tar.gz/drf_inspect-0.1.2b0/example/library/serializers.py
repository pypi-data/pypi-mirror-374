from library.models import Author, Book
from rest_framework import serializers


class AuthorShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('first_name', 'last_name')


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorShortSerializer(many=True)

    class Meta:
        model = Book
        fields = ('pk', 'title', 'authors')


class AuthorSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)
    book_count = serializers.IntegerField()

    class Meta:
        model = Author
        fields = ('pk', 'first_name', 'last_name', 'age', 'books', 'book_count')

        extra_kwargs = {
            'age': {'read_only': True},
        }
