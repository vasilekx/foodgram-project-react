# api/urls.py

from django.urls import include, path
from rest_framework import routers
# from rest_framework.authtoken import views

from .views import (UserViewSet, IngredientViewSet, TagViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')

# router.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet, basename='reviews'
# )
# router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet, basename='comments'
# )
# router.register('genres', GenreViewSet, basename='genres')
# router.register('categories', CategoryViewSet, basename='categories')
# router.register('titles', TitleViewSet, basename='titles')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls), name='api-root'),
]
