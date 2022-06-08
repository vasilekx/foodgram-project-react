# api/views.py

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from foodgram.models import User, Ingredient, Tag, Recipe

from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeCreateSerializer,
    RecipeSerializer
)

# from .filters import TitleFilter
# from .permissions import ReadOnly


class UserViewSet(DjoserUserViewSet):
    """Управление пользователями."""
    # lookup_field = 'username'
    queryset = User.objects.all()
    # permission_classes = (IsAdministrator,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    # @action(
    #     methods=['get'],
    #     detail=False,
    #     url_path='me',
    #     url_name='users_detail',
    #     permission_classes=[permissions.IsAuthenticated],
    #     serializer_class=MeUserSerializer,
    # )
    # def users_detail(self, request):
    #     user = request.user
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('^name', 'name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ['get', 'post', 'patch', 'delete',
                         'head', 'options', 'trace']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return RecipeCreateSerializer
        return self.serializer_class


