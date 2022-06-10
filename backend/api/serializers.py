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
    Ingredient, Tag,
    Recipe, RecipeTag, RecipeIngredient,
    User
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


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'ingredient', 'amount',)
        read_only_fields = ('id', 'ingredient', 'amount',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)
        read_only_fields = ('id', 'name', 'color', 'slug',)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'cooking_time', 'tags',
                  'ingredients', 'is_favorited', 'is_in_shopping_cart',)
        read_only_fields = ('is_favorited', 'is_in_shopping_cart',)

    def get_is_favorited(self, obj):
        return False

    def get_is_in_shopping_cart(self, obj):
        return False


class RecipeCreateSerializer(RecipeSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    # ingredients =

    def to_representation(self, instance):
        data = super(RecipeCreateSerializer, self).to_representation(instance)
        data['tags'] = TagSerializer(instance=instance.tags, many=True).data
        return data

    def validate_tags(self, value):
        """Проверка дублирования тегов."""
        if len(value) != len(set(value)):
            raise serializers.ValidationError('Недопустимо дублирование тегов!')
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            current_tag = get_object_or_404(Tag, pk=tag.pk)
            RecipeTag.objects.create(
                recipe=recipe, tag=current_tag)
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




        # tag_mapping = {tag.id: tag for tag in instance.tags}
        # print(tag_mapping)

        # data_mapping = {tag.id: tag for tag in tags}
        # print(data_mapping)


        # https://clck.ru/qCEtt

        #book_mapping = {book.id: book for book in instance}
        #data_mapping = {item['id']: item for item in validated_data}
        ## Perform creations and updates.
        #ret = []

        #for book_id, data in data_mapping.items():
        #    book = book_mapping.get(book_id, None)
        #    if book is None:
        #        ret.append(self.child.create(data))
        #    else:
        #        ret.append(self.child.update(book, data))

        ## Perform deletions.
        #for book_id, book in book_mapping.items():
        #    if book_id not in data_mapping:
        #        book.delete()


        # for Ingredient

        # def update(self, instance, validated_data):
        #     choices = validated_data.pop('choices')
        #     instance.title = validated_data.get("title", instance.title)
        #     instance.save()
        #     keep_choices = []
        #     for choice in choices:
        #         if "id" in choice.keys():
        #             if Choice.objects.filter(id=choice["id"]).exists():
        #                 c = Choice.objects.get(id=choice["id"])
        #                 c.text = choice.get('text', c.text)
        #                 c.save()
        #                 keep_choices.append(c.id)
        #             else:
        #                 continue
        #         else:
        #             c = Choice.objects.create(**choice, question=instance)
        #             keep_choices.append(c.id)
        #
        #     for choice in instance.choices:
        #         if choice.id not in keep_choices:
        #             choice.delete()

        return super(RecipeCreateSerializer, self).update(instance, validated_data)
