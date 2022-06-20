# foodgram/admin.py

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (Follow, User, Ingredient, Tag, Recipe, RecipeTag,
                     RecipeIngredient, Favorite, ShoppingCart)


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    extra = 0


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    fields = (('name', 'author'),
              'cooking_time', 'text',
              'get_quantity_added_favorites',
              'image')
    readonly_fields = ('get_quantity_added_favorites', 'get_tags')
    list_display = ('pk', 'name', 'author', 'get_tags')
    # list_display_links = ('name', 'text', 'get_tags')
                    # 'tags', 'ingredients')
    # list_editable = ('get_tags',)
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name', 'tags__name')
    empty_value_display = '-пусто-'
    inlines = (RecipeTagInline, RecipeIngredientInline,)

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]
    # get_tags.admin_order_field = 'post__pk'

    def get_quantity_added_favorites(self, obj):
        return obj.favorites.count()

    get_tags.short_description = _('Теги рецепта')
    get_quantity_added_favorites.short_description = _(
        'Добавлений рецепта в избранное'
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe_pk',  'recipe',
                    'ingredient_pk', 'ingredient', 'amount')

    def recipe_pk(self, obj):
        return obj.recipe.pk

    def ingredient_pk(self, obj):
        return obj.ingredient.pk

    recipe_pk.admin_order_field = 'recipe__pk'
    recipe_pk.short_description = _('Ключ рецепта')
    ingredient_pk.short_description = _('Ключ ингредиента')


@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe_pk', 'recipe', 'tag_pk', 'tag',)
    empty_value_display = '-пусто-'

    def recipe_pk(self, obj):
        return obj.recipe.pk

    def tag_pk(self, obj):
        return obj.tag.pk

    recipe_pk.admin_order_field = 'recipe__pk'
    recipe_pk.short_description = _('Ключ рецепта')
    tag_pk.short_description = _('Ключ тега')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author',)
    ordering = ('-pk',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    ordering = ('-pk',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe',)
    ordering = ('-pk',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    ordering = ('-pk',)
