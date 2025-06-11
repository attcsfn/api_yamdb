from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name')
        read_only_fields = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('id', 'name')
        read_only_fields = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(
        slug_field='slug',
        many=True,
        read_only=True
    )
    category = SlugRelatedField(
        slug_field='slug',
        read_only=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        read_only_fields = ('id',)
