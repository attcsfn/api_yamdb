from rest_framework import viewsets

from reviews.models import Category, Genre, Title
from .serializers import (CategorySerializer, GenreSerializer, TitleSerializer)


class CategoryViewSet(viewsets.ModelViewSet):
    """API для работы с Категориями"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    """API для работы с Жанрами"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """API для работы с Произведениями"""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
