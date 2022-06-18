# api/serializers.py

from django.conf import settings
from django.shortcuts import get_list_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from foodgram.models import (
    Ingredient, Tag, Follow,
    Recipe, RecipeTag, RecipeIngredient,
    User, Favorite, ShoppingCart
)
from foodgram.validators import validate_username
from .validators import validate_ingredients


class MixinUserSerializer:
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
        )


class UserSerializer(MixinUserSerializer, DjoserUserSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(MixinUserSerializer.Meta):
        fields = MixinUserSerializer.Meta.fields + ('is_subscribed',)
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated and user != obj:
            status = user.following.filter(user=obj).exists()
        else:
            status = False
        return status


class UserCreateSerializer(MixinUserSerializer, DjoserUserCreateSerializer):

    class Meta(MixinUserSerializer.Meta):
        pass

    def validate_username(self, value):
        validate_username(value)
        return value


class FavoriteOrShoppingCartRecipeSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    # image = serializers.ReadOnlyField(source='recipe.image')

    class Meta:
        fields = ('id', 'name', 'cooking_time',) # 'image'


class FollowRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time',) # 'image'


class FollowSerializer(serializers.Serializer):
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

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('id', 'name', 'measurement_unit',)


# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
#         read_only=True,
#         source='ingredient'
#     )
#     name = serializers.SlugRelatedField(
#         read_only=True,
#         slug_field='name',
#         source='ingredient'
#     )
#     measurement_unit = serializers.SlugRelatedField(
#         read_only=True,
#         slug_field='measurement_unit',
#         source='ingredient'
#     )
#
#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'name', 'measurement_unit', 'amount',)
#         # read_only_fields = ( 'amount',)

class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AmountIngredient."""
    name = serializers.ReadOnlyField()
    measurement_unit = serializers.ReadOnlyField()
    amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        print(obj.recipeingredient_set)
        recipeingredient_set = obj.recipeingredient_set
        obj = get_object_or_404(
            obj.recipeingredient_set,
            ingredient_id=obj.id,
            recipe_id=self.context.get('id')
        ).amount
        return obj


class RecipeSerializer(serializers.ModelSerializer):
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
            'ingredients',
            'name',
            'text',
            'author',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
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
        # data['ingredients'] = RecipeIngredientSerializer(
        #     instance=instance.ingredients,
        #     many=True
        # ).data
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
