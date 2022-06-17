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
from rest_framework.request import Request
from djoser.views import UserViewSet as DjoserUserViewSet


from foodgram.models import (User, Ingredient, Tag, Recipe,
                             Follow, Favorite, ShoppingCart)


from .serializers import (
    IngredientSerializer,
    TagSerializer,
    # RecipeCreateSerializer,
    RecipeSerializer,
    FollowSerializer,
    FavoriteOrShoppingCartRecipeSerializer
)

from .permissions import IsOwnerOrReadOnly, IsOwner
from .utilities import (delete_object, response_created_object,
                        create_or_delete_favorite_or_purchase_recipe)
from .filter import RecipeFilter


class UserViewSet(DjoserUserViewSet):
    """Управление пользователями."""
    queryset = User.objects.all()
    lookup_field = 'pk'
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

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsOwner],
        serializer_class=FollowSerializer,
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        fields = {'user': request.user, 'author': author}
        if_already_exists = Follow.objects.filter(**fields).exists()
        if request.method == 'DELETE':
            return delete_object(
                model=Follow,
                fields=fields,
                exist=if_already_exists,
                errors_message=_('Вы еще не подписаны!'),
            )
        return response_created_object(
            model=Follow,
            fields=fields,
            exist=bool(if_already_exists or request.user == author),
            errors_message=_('Вы уже подписаны или пытаетесь '
                             'подписатьсяна самого себя.'),
            serializer_class=self.get_serializer_class(),
            context={'request': request}
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsOwner],
        serializer_class=FollowSerializer,
    )
    def subscriptions(self, request):
        user = request.user.follower.all()
        page = self.paginate_queryset(user)
        serializer = self.get_serializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('^name', 'name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete',
                         'head', 'options', 'trace']
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsOwner],
    )
    def favorite(self, request, pk=None):
        return create_or_delete_favorite_or_purchase_recipe(
            request=request,
            pk_object=pk,
            model_object=Favorite,
            model_recipe=Recipe,
            serializer_class=FavoriteOrShoppingCartRecipeSerializer,
            post_errors_message=_('Рецепт уже добавлен в избранное!'),
            delete_errors_message=_('Рецепт ещё не добавлен в избранное!')
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsOwner],
    )
    def shopping_cart(self, request, pk=None):
        return create_or_delete_favorite_or_purchase_recipe(
            request=request,
            pk_object=pk,
            model_object=ShoppingCart,
            model_recipe=Recipe,
            serializer_class=FavoriteOrShoppingCartRecipeSerializer,
            post_errors_message=_('Рецепт уже добавлен в список покупок!'),
            delete_errors_message=_('Рецепт ещё не добавлен в список покупок!')
        )
