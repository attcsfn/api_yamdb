from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api_yamdb import constants
from api.validators import validate_year
from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        max_length=constants.LIMIT_EMAIL
    )
    username = serializers.CharField(
        required=True,
        max_length=constants.LIMIT_USERNAME,
        validators=[RegexValidator(
            regex=constants.USERNAME_REGEX,
            message='Недопустимые символы в username!'
        )],
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
        email_owner = User.objects.filter(email=email).first()
        username_owner = User.objects.filter(username=username).first()

        if email_owner and email_owner.username != username:
            raise serializers.ValidationError({
                'email': 'Этот email уже используется для другого аккаунта!'
            })
        if username_owner and username_owner.email != email:
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
    username = serializers.CharField(
        required=True, max_length=constants.LIMIT_USERNAME
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
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'email': {'required': True},
        }


class UserMeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'email': {'required': True},
        }


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор объектов модели Category."""

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор объектов модели Genre."""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGETSerializer(ReadOnlyModelSerializer):
    """Сериализатор объектов модели Title для GET запросов."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'rating',
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор объектов модели Title."""

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
            'name',
            'year',
            'description',
            'genre',
            'category',
        )

    def to_representation(self, title):
        return TitleGETSerializer(title).data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review',)


class ReviewSerializer(serializers.ModelSerializer):
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

        if request.method != 'POST':
            return data

        if Review.objects.filter(title_id=title_id, author=user).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение.'
            )
        return data
