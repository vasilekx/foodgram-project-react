# api/urls.py

from django.urls import include, path
from rest_framework import routers

from .views import (
    UserViewSet, IngredientViewSet, TagViewSet, RecipeViewSet
)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls), name='api-root'),
]
