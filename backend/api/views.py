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

from foodgram.models import User

# from .filters import TitleFilter
# from .permissions import

from .serializers import UserSerializer, MeUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Управление пользователями."""
    # lookup_field = 'username'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (IsAdministrator,)
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    @action(
        methods=['get'],
        detail=False,
        url_path='me',
        url_name='users_detail',
        # permission_classes=[permissions.IsAuthenticated],
        serializer_class=MeUserSerializer,
    )
    def users_detail(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

