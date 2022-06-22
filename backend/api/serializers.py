# api/serializers.py

import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)

from foodgram.models import (
    Ingredient, Tag, Follow,
    Recipe, RecipeTag, RecipeIngredient,
    User
)

from users.validators import validate_username

from .validators import validate_ingredients


class MixinUserSerializer:
    """Mixin для модели User."""
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
        )


class UserSerializer(MixinUserSerializer, DjoserUserSerializer):
    """Сериализатор для модели User."""
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(MixinUserSerializer.Meta):
        fields = MixinUserSerializer.Meta.fields + ('is_subscribed',)
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated and user != obj:
            status = user.follower.filter(author=obj).exists()
        else:
            status = False
        return status


class UserCreateSerializer(MixinUserSerializer, DjoserUserCreateSerializer):
    """Сериализатор создания модели User."""
    class Meta(MixinUserSerializer.Meta):
        pass

    def validate_username(self, value):
        validate_username(value)
        return value


class FavoriteOrShoppingCartRecipeSerializer(serializers.Serializer):
    """
    Сериализатор для отображения модели Recipe
    при добавление в избранное/список покупок.
    """
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    image = serializers.ImageField(source='recipe.image', read_only=True)

    class Meta:
        fields = ('id', 'name', 'cooking_time', 'image')


class FollowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения модели Recipe при подписки."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class FollowSerializer(serializers.Serializer):
    """Сериализатор для модели Follow."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user.id
        queryset = Follow.objects.filter(
            user=request_user,
            author=obj.author
        ).exists()
        return queryset

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = int(self.context.get('request').query_params.get(
            'recipes_limit', 0
        ))
        return obj.author.recipes.all()[:recipes_limit]

    def to_representation(self, instance):
        data = super(FollowSerializer, self).to_representation(instance)
        data['recipes'] = FollowRecipeSerializer(
            instance=data.get('recipes'),
            many=True
        ).data
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AmountIngredient."""
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        obj = get_object_or_404(
            obj.recipeingredient_set,
            ingredient_id=obj.id,
            recipe_id=self.context.get('id')
        ).amount
        return obj


class Base64ImageField(serializers.ImageField):
    """
    Пользовательское поле изображения -
    обрабатывает изображения в кодировке base64.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(
                base64.b64decode(imgstr),
                name=id.urn[9:] + '.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'text',
            'author',
            'cooking_time',
            'image',
            'is_favorited',
            'is_in_shopping_cart',
            'tags',
            'ingredients',
        )
        read_only_fields = ('is_favorited', 'is_in_shopping_cart',)

    def get_ingredients(self, value):
        """Получение ключа ingredients."""
        ingredient_list = RecipeIngredientSerializer(
            value.ingredients.all(),
            many=True,
            read_only=True,
            context={'id': value.id}
        ).data
        return ingredient_list

    def current_user(self):
        return self.context.get('request').user

    def get_is_favorited(self, obj):
        if self.current_user().is_authenticated:
            return Recipe.objects.filter(
                id=obj.id,
                favorites__user=self.current_user()
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.current_user().is_authenticated:
            return Recipe.objects.filter(
                id=obj.id,
                purchases__user=self.current_user()
            ).exists()
        return False

    def to_representation(self, instance):
        data = super(RecipeSerializer, self).to_representation(instance)
        data['tags'] = TagSerializer(instance=instance.tags, many=True).data
        return data

    def validate_tags(self, value):
        """Проверка дублирования тегов."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Недопустимо дублирование тегов.')
        return value

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not validate_ingredients(ingredients):
            raise serializers.ValidationError(
                {'ingredients': 'Невозможно провести валидацию.'}
            )
        data['ingredients'] = ingredients
        return data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            RecipeTag.objects.create(
                recipe=recipe,
                tag=current_tag
            )
        for recipe_ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=recipe_ingredient.get('id'),
                amount=recipe_ingredient.get('amount')
            )
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        tags = list(instance.tags.all())
        ingredients_data = validated_data.pop('ingredients')
        ingredients = list(instance.ingredients.values_list('id', flat=True))
        for tag in tags_data:
            if tag in tags:
                tags.remove(tag)
                print(tags)
            else:
                RecipeTag.objects.create(recipe=instance, tag=tag)
        if tags:
            for tag in tags:
                get_object_or_404(
                    RecipeTag,
                    recipe=instance,
                    tag=tag
                ).delete()
        for ingredient in ingredients_data:
            id, amount = ingredient.values()
            if id in ingredients:
                RecipeIngredient.objects.filter(
                    recipe_id=instance.id,
                    ingredient_id=id
                ).update(amount=amount)
                ingredients.remove(id)
            else:
                instance.ingredients.add(
                    id, through_defaults={'amount': amount}
                )
        if ingredients:
            instance.ingredients.remove(*ingredients)

        return super(RecipeSerializer, self).update(instance, validated_data)
