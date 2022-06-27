from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

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
        # context = self.context
        # print(context)
        # request = self.context.get('request')
        # print(request)
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
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

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
    # id = serializers.IntegerField(source='ingredient.id')

    # it work
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    # it work
    # id = serializers.SlugRelatedField(
    #     many=False,
    #     slug_field='id',
    #     queryset=Ingredient.objects.all()
    # )
    # id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    # amount = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    # def get_amount(self, obj):
    #     obj = get_object_or_404(
    #         obj.recipeingredient_set,
    #         ingredient_id=obj.id,
    #         recipe_id=self.context.get('id')
    #     ).amount
    #     return obj


class AmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(source='recipeingredient_set')

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')
        # extra_kwargs = {'id': {'write_only': True}}


class RecipeIngredient2Serializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(source='ingredient.id')

    # it work
    # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    # it work
    # id = serializers.SlugRelatedField(
    #     many=False,
    #     slug_field='id',
    #     queryset=Ingredient.objects.all()
    # )
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    # amount = serializers.SerializerMethodField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    # def get_amount(self, obj):
    #     obj = get_object_or_404(
    #         obj.recipeingredient_set,
    #         ingredient_id=obj.id,
    #         recipe_id=self.context.get('id')
    #     ).amount
    #     return obj


class AmountIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(source='recipeingredient_set')

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')
        # extra_kwargs = {'id': {'write_only': True}}


class RecipeViewSerializer(serializers.Serializer):

    # tags = TagSerializer(many=True, read_only=True)
    #

    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    text = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)

    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        # model = Recipe
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
        # read_only_fields = ('is_favorited', 'is_in_shopping_cart',)

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


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    # ingredients = AmountIngredientSerializer(many=True)
    ingredients = RecipeIngredient2Serializer(many=True,
                                              source='recipeingredient_set')
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

    # def get_ingredients(self, value):
    #     return RecipeIngredientSerializer(
    #         value.ingredients.all(),
    #         many=True,
    #         read_only=True,
    #         context={'id': value.id}
    #     ).data

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
        # in1 = instance
        # in_list = self.initial_data.get['ingredients']

        data = super(RecipeSerializer, self).to_representation(instance)
        data['tags'] = TagSerializer(instance=instance.tags, many=True).data
        # data = RecipeViewSerializer

        # другой serializers
        # context = self.context
        # print(context)
        # inst = instance
        # ser = RecipeViewSerializer(inst, context=self.context)
        # data = ser.data

        return data

    def validate_tags(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Недопустимо дублирование тегов.'
            )
        return value

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        # ingredients_data = data.get('ingredients')
        ingredients_data = data.get('recipeingredient_set')
        print(f'{ingredients=}')
        print(f'{ingredients_data=}')

        print(ingredients_data)
        if not validate_ingredients(ingredients_data):
            raise serializers.ValidationError(
                {'ingredients': 'Невозможно провести валидацию.'}
            )
        # data['ingredients'] = ingredients
        return super().validate(data)
        # return data

    def create_tags(self, tags, recipe_object):
        RecipeTag.objects.bulk_create(
            [RecipeTag(recipe=recipe_object, tag=tag) for tag in tags]
        )

    def create_ingredients(self, ingredients, recipe_object):
        # in1 = ingredients
        # in_pop = in1[0]['ingredients']
        # for i in ingredients:
        #     t = i['ingredient'].get('id')

        # ingredients_list = [dict(ingredient) for ingredient in ingredients]
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
        # ingredients = validated_data.pop('ingredients')
        ingredients = validated_data.pop('recipeingredient_set')
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        # RecipeTag.objects.bulk_create(
        #     [RecipeTag(recipe=recipe, tag=tag) for tag in tags]
        # )
        # RecipeIngredient.objects.bulk_create(
        #     [
        #         RecipeIngredient(
        #             recipe=recipe,
        #             ingredient=recipe_ingredient.get('id'),
        #             amount=recipe_ingredient.get('amount')
        #         ) for recipe_ingredient in ingredients_list
        #     ]
        # )

        # 7787407
        # https://github.com/vasilekx/foodgram-project-react/blob/7787407bf65b08f7612f65a772561dc988f3ad24/backend/api/serializers.py

        return recipe

    def update(self, instance, validated_data):
        # tags_data = validated_data.pop('tags')
        # tags = list(instance.tags.all())
        # ingredients_data = validated_data.pop('ingredients')
        # ingredients = list(instance.ingredients.values_list('id', flat=True))

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient_set')
        # ingredients = [
        #     dict(ingredient)
        #     for ingredient in validated_data.pop('ingredients')
        # ]

        # Очистка тегов и ингридиентов
        instance.tags.clear()
        instance.ingredients.clear()

        # Создание новых тегов и ингридиентов
        self.create_tags(tags, instance)
        self.create_ingredients(ingredients, instance)

        # for tag in tags_data:
        #     if tag in tags:
        #         tags.remove(tag)
        #     else:
        #         RecipeTag.objects.create(recipe=instance, tag=tag)
        # if tags:
        #     for tag in tags:
        #         get_object_or_404(
        #             RecipeTag,
        #             recipe=instance,
        #             tag=tag
        #         ).delete()
        # for ingredient in ingredients_data:
        #     pk, amount = ingredient.values()
        #     if pk in ingredients:
        #         RecipeIngredient.objects.filter(
        #             recipe_id=instance.pk,
        #             ingredient_id=pk
        #         ).update(amount=amount)
        #         ingredients.remove(pk)
        #     else:
        #         instance.ingredients.add(
        #             pk, through_defaults={'amount': amount}
        #         )
        # if ingredients:
        #     instance.ingredients.remove(*ingredients)

        return super(RecipeSerializer, self).update(instance, validated_data)
