# api/urls.py

from django.urls import include, path
from rest_framework import routers

from .views import (UserViewSet)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

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
# router.register(r'users', UserViewSet, basename='user')

auth_urlpatterns = [
    # path('signup/', signup, name='signup'),
    # path('token/', token, name='token'),
]
# http://127.0.0.1/api/users/set_password/
users_urlpatterns = []

urlpatterns = [
    path('users/set_password/', include(users_urlpatterns)),  # ???
    path('auth/', include(auth_urlpatterns)),  # auth/token/
    path('', include(router.urls)),
]