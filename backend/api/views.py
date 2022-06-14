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

# from .filters import TitleFilter
from .permissions import IsOwnerOrReadOnly
from .viewsets import CreateDestroyListViewSet


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

    def subscribe(self):
        pass

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        # url_name='users_detail',
        permission_classes=[permissions.IsAuthenticated],
        # serializer_class=MeUserSerializer,
    )
    def subscribes(self, request):
        author = get_object_or_404(User, id=self.kwargs.get('user_id'))
        if request.method == 'POST':
            if_already_exists = Follow.objects.filter(
                user=request.user,
                author=author,
            ).exists()
            if if_already_exists or request.user == author:
                return Response(
                    {
                        'errors': ('Вы уже подписаны или пытаетесь '
                                   'подписатьсяна самого себя.')
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            new_sub = Follow.objects.create(
                user=request.user,
                author=author,
            )
            serializer = FollowSerializer(
                new_sub,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Follow,
                          user=request.user,
                          author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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


# class FollowViewSet(viewsets.ModelViewSet):
#     serializer_class = FollowSerializer
#     permission_classes = (IsOwnerOrReadOnly,)
#     # filter_backends = (filters.SearchFilter,)
#     # search_fields = ('following__username',)
#
#     def get_user(self):
#         return get_object_or_404(User, pk=self.kwargs.get('user_id'))
#
#     def get_queryset(self):
#         return self.request.user.follower.all()
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user, author=self.get_user())
#
#     def perform_destroy(self, instance):
#         instance.delete()
