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
        return False


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
        model = Favorite
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
    # tags = TagSerializer(many=True, read_only=True)
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
        print(value.ingredients.all())
        ingredients_all = value.ingredients.all()
        ingredient_list = RecipeIngredientSerializer(
            value.ingredients.all(),
            many=True,
            read_only=True,
            context={'id': value.id}
        ).data
        return ingredient_list

    def get_is_favorited(self, obj):
        return Recipe.objects.filter(
            id=obj.id,
            favorites__user=self.context.get('request').user
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        return Recipe.objects.filter(
            id=obj.id,
            purchases__user=self.context.get('request').user
        ).exists()

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
        if not ingredients:
            raise serializers.ValidationError(
                {
                    'ingredients': 'Обязательное поле.'
                }
            )
        ingredient_list = []
        for ingredient_item in ingredients:
            ingredient = Ingredient.objects.filter(
                id=ingredient_item.get('id')
            )
            if not ingredient:
                raise serializers.ValidationError(
                    {
                        'ingredients': {
                            'id': (
                                'Ингридиента не существует.'
                            )
                        }
                    }
                )
            ingredient = ingredient.get()
            # ingredient = get_object_or_404(Ingredient, id=ingredient_item['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'Недопустимо дублирование ингридиентов.'
                )
            ingredient_list.append(ingredient)
            if int(ingredient_item['amount']) < 0:
                raise serializers.ValidationError(
                    {
                        'ingredients': {
                            'amount': (
                                'Количества ингредиента меньше 0.'
                            )
                        }
                    }
                )

        data['ingredients'] = ingredients
        print(data)
        return data

    def create(self, validated_data):
        initial_data = self.initial_data
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        #ingredients_list = [dict(ingredient) for ingredient in ingredients]
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
        tags_data: list = validated_data.pop('tags')
        tags: list = list(instance.tags.all())
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

        return super(RecipeSerializer, self).update(instance, validated_data)



# class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
#         queryset=Ingredient.objects.all(),
#     )
#
#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'amount',)
#
#
# class RecipeCreateSerializer(RecipeSerializer):
#     tags = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=Tag.objects.all(),
#     )
#     # ingredients = RecipeIngredientCreateSerializer(
#     #     many=True,
#     # )
#     ingredients = serializers.SerializerMethodField()
#
#     def get_ingredients(self, obj):
#         p_obj = obj
#         p_obj_all = obj.ingredients.all()
#         return p_obj_all
#
#     def validate(self, data):
#         print('validate')
#         print(self.initial_data)
#         ingredients = data['ingredients']
#         return data
#
#     def to_representation(self, instance):
#         data = super(RecipeCreateSerializer, self).to_representation(instance)
#         data['tags'] = TagSerializer(instance=instance.tags, many=True).data
#         data['ingredients'] = RecipeIngredientSerializer(
#             instance=instance.ingredients,
#             many=True
#         ).data
#         return data
#
#     def validate_tags(self, value):
#         """Проверка дублирования тегов."""
#         if len(value) != len(set(value)):
#             raise serializers.ValidationError('Недопустимо дублирование тегов!')
#         return value
#
#     def create(self, validated_data):
#         initial_data = self.initial_data
#         tags = validated_data.pop('tags')
#         ingredients = validated_data.pop('ingredients')
#         ingredients_list = [dict(ingredient) for ingredient in ingredients]
#         recipe = Recipe.objects.create(**validated_data)
#         for tag in tags:
#             current_tag = get_object_or_404(Tag, pk=tag.pk)
#             RecipeTag.objects.create(
#                 recipe=recipe,
#                 tag=current_tag
#             )
#         for recipe_ingredient in ingredients_list:
#             RecipeIngredient.objects.create(
#                 recipe=recipe,
#                 ingredient=recipe_ingredient.get('id'),
#                 amount=recipe_ingredient.get('amount')
#             )
#         return recipe
#
#     def update(self, instance, validated_data):
#         tags_data: list = validated_data.pop('tags')
#         tags: list = list(instance.tags.all())
#         for tag in tags_data:
#             if tag in tags:
#                 tags.remove(tag)
#                 print(tags)
#             else:
#                 RecipeTag.objects.create(recipe=instance, tag=tag)
#         if tags:
#             for tag in tags:
#                 get_object_or_404(
#                     RecipeTag,
#                     recipe=instance,
#                     tag=tag
#                 ).delete()
#
#         return super(RecipeCreateSerializer, self).update(instance,
#                                                           validated_data)
