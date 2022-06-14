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
    # fields = ('pk', 'name', 'text', 'author', 'cooking_time', 'get_tags',)
    list_display = ('pk', 'name', 'author', 'get_tags',)
    # list_display_links = ('name', 'text', 'get_tags')
                    # 'tags', 'ingredients')
    # list_editable = ('get_tags',)
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name', 'tags__name')
    empty_value_display = '-пусто-'
    inlines = (RecipeTagInline, RecipeIngredientInline,)

    def get_tags(self, obj):
        return [tag.tag.name for tag in RecipeTag.objects.filter(recipe=obj)]
    # get_tags.admin_order_field = 'post__pk'
    get_tags.short_description = _('Теги рецепта')

    # def _tags(self, obj):
    #     return obj.tags.all()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email', 'first_name', 'last_name', )
    search_fields = ('username', 'email', 'first_name', 'last_name',)
    list_filter = ('username', 'email', 'first_name')
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe_pk',  'recipe', 'ingredient', 'amount')
    empty_value_display = '-пусто-'

    def recipe_pk(self, obj):
        return obj.recipe.pk

    recipe_pk.admin_order_field = 'recipe__pk'
    recipe_pk.short_description = _('Ключ рецепта')


# admin.site.register(User)
admin.site.register(Follow)
# admin.site.register(Ingredient)
admin.site.register(Tag)
# admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTag)
# admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
