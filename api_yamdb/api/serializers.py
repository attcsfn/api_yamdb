from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import SlugRelatedField

from api.validators import validate_score_range, validate_year
from api_yamdb import constants
from reviews.models import Comment, Review
from titles.models import Category, Genre, Title
from users.models import User


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
        )]
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
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения!'}
            )

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=False,
        default=User.USER
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'bio', 'role'
        )
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_role(self, value):
        if value not in dict(User.ROLE_CHOICES):
            raise serializers.ValidationError("Недопустимая роль")
        return value
