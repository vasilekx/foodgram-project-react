from django.db.models import Case, IntegerField, Q, Sum, Value, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.models import (Favorite, Follow, Ingredient, Recipe,
                             ShoppingCart, Tag, User)
from .filter import RecipeFilter
from .permissions import IsOwner, IsOwnerOrReadOnly
from .serializers import (FavoriteOrShoppingCartRecipeSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer)
from .utilities import (create_or_delete_favorite_or_purchase_recipe,
                        delete_object, response_created_object)


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    lookup_field = 'pk'

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
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    INGREDIENT_SEARCH_PARAM = 'name'

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        keywords = self.request.query_params.get(self.INGREDIENT_SEARCH_PARAM)
        if keywords:
            at_beginning = Q(name__regex=fr'^{keywords}')
            anywhere = Q(name__regex=fr'{keywords}')
            search_type_ordering_expression = Case(
                When(at_beginning, then=Value(1)),
                When(anywhere, then=Value(0)),
                default=Value(-1),
                output_field=IntegerField()
            )
            queryset = queryset.filter(at_beginning | anywhere).annotate(
                search_type_ordering=search_type_ordering_expression
            ).distinct().order_by('-search_type_ordering')
        return queryset


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

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[permissions.AllowAny],
    )
    def download_shopping_cart(self, request):
        user = request.user
        purchases_data = user.purchases.all().select_related(
            'recipe'
        ).order_by(
            'recipe__ingredients__name'
        ).values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(
            amount=Sum('recipe__recipeingredient__amount')
        )
        if not purchases_data:
            return Response(
                {
                    'error': _('Ваш список покупок пуст!')
                },
                status=status.HTTP_404_NOT_FOUND
            )
        purchases_text = 'Продуктовый помощник\nСписок покупок\n\n'
        for item in purchases_data:
            ingredient, measurement_unit, amount = item.values()
            purchases_text += f'{ingredient} - {amount}({measurement_unit})\n'
        response = HttpResponse(purchases_text, content_type='text/plain')
        filename = 'shopping_list.txt'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
