from http import HTTPStatus

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import mixins, pagination, views, viewsets
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
                          UserSerializer)


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
    queryset = Title.objects.annotate(rating=Avg('reviews__score')
                                      ).order_by('-rating')
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filterset_class = TitleFilter
    filterset_fields = ('name',)
    ordering = ('name',)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleGETSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с отзывами (Reviews)."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly)

    def get_queryset(self):
        return Review.objects.filter(title_id=self.kwargs['title_id'])

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs['title_id'])

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с комментариями к отзывам."""

    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAuthorModeratorAdminOrReadOnly)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs['review_id'],
            title_id=self.kwargs['title_id']
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)


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
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=user.role)
            return Response(serializer.data, status=HTTPStatus.OK)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=HTTPStatus.OK)
