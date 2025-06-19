from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api_yamdb import constants
from api.validators import validate_year
from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователей."""

    email = serializers.EmailField(
        required=True,
        max_length=constants.LIMIT_EMAIL
    )
    username = serializers.CharField(
        required=True,
        max_length=constants.LIMIT_USERNAME,
        validators=[
            RegexValidator(
                regex=constants.USERNAME_REGEX,
                message='Недопустимые символы в username!'
            )
        ],
    )

    def validate_username(self, value):
        if value == constants.UNAVAILABLE_USERNAME:
            raise serializers.ValidationError(
                f"Нельзя использовать {value} как username!"
            )
        return value

    def validate(self, data):
        email = data['email']
        username = data['username']

        existing_user = User.objects.filter(
            Q(email=email) | Q(username=username)
        ).first()

        if existing_user:
            if (existing_user.email == email
               and existing_user.username != username):
                raise serializers.ValidationError({
                    'email': 'Этот email уже используется для другого аккаунта!'
                })
            if (existing_user.username == username
               and existing_user.email != email):
                raise serializers.ValidationError({
                    'username': 'Этот username уже занят другим пользователем!'
                })
        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            subject='Ваш код подтверждения YAmdb!',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[validated_data['email']],
            fail_silently=False,
        )
        return user


class TokenSerializer(serializers.Serializer):
    """Сериализатор для получения JWT-токена."""

    username = serializers.CharField(
        required=True,
        max_length=constants.LIMIT_USERNAME
    )
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data['username']
        confirmation_code = data['confirmation_code']
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения!'},
            )

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'email': {'required': True},
        }


class UserMeSerializer(UserSerializer):
    """Сериализатор для профиля текущего пользователя."""

    class Meta(UserSerializer.Meta):
        extra_kwargs = {
            **UserSerializer.Meta.extra_kwargs,
            'role': {'read_only': True},
        }


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGETSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description',
            'genre', 'category', 'rating'
        )
        read_only_fields = fields

    def get_rating(self, obj):
        if hasattr(obj, 'rating'):
            return int(obj.rating) if obj.rating is not None else None
        return None


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления произведений."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=True,
        allow_empty=False,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    year = serializers.IntegerField(validators=[validate_year])

    class Meta:
        model = Title
        fields = (
            'name', 'year', 'description', 'genre', 'category'
        )

    def to_representation(self, instance):
        """Используем GET-сериализатор для представления данных."""
        return TitleGETSerializer(instance).data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    score = serializers.IntegerField(
        min_value=1,
        max_value=10,
        error_messages={
            'min_value': 'Оценка не может быть ниже 1.',
            'max_value': 'Оценка не может быть выше 10.'
        }
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('title',)

    def validate(self, data):
        """Проверка: один отзыв на одно произведение от одного пользователя."""
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        user = request.user

        if request.method == 'POST':
            if Review.objects.filter(
                title_id=title_id, author=user
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв на это произведение.'
                )
        return data
