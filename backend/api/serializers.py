from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from rest_framework import serializers

from foodgram.models import (
    Follow, Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag, User
)
from users.validators import validate_username

from .fields import Base64ImageField
from .validators import validate_ingredients


class MixinUserSerializer:
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'password',)


class UserSerializer(MixinUserSerializer, DjoserUserSerializer):
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
    class Meta(MixinUserSerializer.Meta):
        pass

    def validate_username(self, value):
        validate_username(value)
        return value


class FavoriteOrShoppingCartRecipeSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    image = serializers.ImageField(source='recipe.image', read_only=True)

    class Meta:
        fields = ('id', 'name', 'cooking_time', 'image')


class FollowRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


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
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user.id
        return Follow.objects.filter(
            user=request_user,
            author=obj.author
        ).exists()

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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipeingredient_set')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'cooking_time', 'image',
                  'is_favorited', 'is_in_shopping_cart', 'tags',
                  'ingredients',)
        read_only_fields = ('is_favorited', 'is_in_shopping_cart',)

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
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Недопустимо дублирование тегов.'
            )
        return value

    def validate(self, data):
        if not validate_ingredients(data.get('recipeingredient_set')):
            raise serializers.ValidationError(
                {'ingredients': 'Невозможно провести валидацию.'}
            )
        return super().validate(data)

    def create_tags(self, tags, recipe_object):
        RecipeTag.objects.bulk_create(
            [RecipeTag(recipe=recipe_object, tag=tag) for tag in tags]
        )

    def create_ingredients(self, ingredients, recipe_object):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe_object,
                    ingredient_id=recipe_ingredient['ingredient']['id'],
                    amount=recipe_ingredient['amount']
                ) for recipe_ingredient in ingredients
            ]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        instance.tags.clear()
        instance.ingredients.clear()
        self.create_tags(tags, instance)
        self.create_ingredients(ingredients, instance)
        return super(RecipeSerializer, self).update(instance, validated_data)
