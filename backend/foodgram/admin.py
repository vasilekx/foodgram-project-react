# foodgram/admin.py

from django.contrib import admin

from .models import (Follow, User, Ingredient, Tag, Recipe, RecipeTag,
                     RecipeIngredient, Favorite, ShoppingCart)

admin.site.register(User)
admin.site.register(Follow)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(RecipeTag)
admin.site.register(RecipeIngredient)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
