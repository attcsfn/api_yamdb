from http import HTTPStatus

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, pagination, views, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Review
from titles.models import Category, Genre, Title
from users.models import User
from users.permissions import (IsAdmin, IsAdminOrReadOnly,
                               IsAuthorModeratorAdminOrReadOnly)

from .filters import TitleFilter
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleGETSerializer, TitleSerializer, TokenSerializer,
                          UserSerializer, UserMeSerializer)


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().order_by('name')
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    )
    filterset_class = TitleFilter
    filterset_fields = ('name', 'category', 'genre', 'year')
    ordering_fields = ('name', 'year', 'rating')
    ordering = ('name',)

    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        return Title.objects.annotate(rating=Avg('reviews__score')).order_by(
            'name')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGETSerializer
        return TitleSerializer


class SignUpView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.OK)


class TokenObtainView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = str(AccessToken.for_user(user))
        return Response({'token': token}, status=HTTPStatus.OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        search = self.request.query_params.get('search')
        if search:
            return self.queryset.filter(username__icontains=search)
        return self.queryset

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = UserMeSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.OK)
        serializer = UserMeSerializer(user)
        return Response(serializer.data, status=HTTPStatus.OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly)
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_review(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title_id=title_id)
        return review

    def get_queryset(self):
        return self.get_review().comments.all().order_by('-pub_date')

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorModeratorAdminOrReadOnly,
    )
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all().order_by('-pub_date')

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)
