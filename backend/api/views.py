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

from foodgram.models import (User, Ingredient, Tag, Recipe, RecipeIngredient,
                             Follow)


from .serializers import (
    IngredientSerializer,
    TagSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
    FollowSerializer
)

from .permissions import IsOwnerOrReadOnly


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

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=FollowSerializer,
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        if_already_exists = Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()
        if request.method == 'DELETE':
            if not if_already_exists:
                return Response(
                    {
                        'errors': ('Вы еще не подписаны!')
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            get_object_or_404(Follow,
                              user=request.user,
                              author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if if_already_exists or request.user == author:
            return Response(
                {
                    'errors': ('Вы уже подписаны или пытаетесь '
                               'подписатьсяна самого себя.')
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        new_follower = Follow.objects.create(user=request.user, author=author)
        serializer = self.get_serializer(
            new_follower,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
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
    permission_classes = (IsOwnerOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete',
                         'head', 'options', 'trace']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return RecipeCreateSerializer
        return self.serializer_class
