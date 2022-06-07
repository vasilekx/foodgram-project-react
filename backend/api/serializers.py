# api/serializers.py

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from rest_framework.generics import get_object_or_404

from foodgram.models import User, Ingredient, Tag, Recipe, RecipeTag
from foodgram.validators import validate_username


class MixinUserSerializer:
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',

        )
        read_only_fields = ('is_subscribed',)


class UserSerializer(MixinUserSerializer, DjoserUserSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(MixinUserSerializer.Meta):
        fields = MixinUserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, obj):
        return False


class UserCreateSerializer(MixinUserSerializer, DjoserUserCreateSerializer):

    class Meta(MixinUserSerializer.Meta):
        pass

    def validate_username(self, value):
        validate_username(value)
        return value


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('id', 'name', 'measurement_unit',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('id', 'name', 'color', 'slug',)


class CreateRecipeTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id',)
        read_only_fields = ('id',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    # author = serializers.SlugRelatedField(
    #     slug_field='username',
    #     read_only=True,
    #     default=serializers.CurrentUserDefault()
    # )

    # tags = serializers.PrimaryKeyRelatedField(many=True,
    #                                           queryset=Tag.objects.all())
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'cooking_time', 'tags')
        read_only_fields = ('author',)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            # Создадим новую запись или получим существующий экземпляр из БД
            pk = tag.pk
            # current_tag = Tag.objects.get(pk=tag.pk)
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            # Поместим ссылку на каждое достижение во вспомогательную таблицу
            # Не забыв указать к какому котику оно относится
            RecipeTag.objects.create(
                recipe=recipe, tag=current_tag)
        return recipe

    # def update(self, instance, validated_data):
    #     return 0


class RecipeGetSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'cooking_time', 'tags')
        read_only_fields = ('author',)
