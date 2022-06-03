# api/serializers.py

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
    UserSerializer as DjoserUserSerializer
)

from foodgram.models import User, Ingredient
from foodgram.validators import validate_username


class MixinUserSerializer:
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',

        )
        read_only_fields = ('is_subscribed',)


class UserSerializer(MixinUserSerializer, DjoserUserSerializer):
    password = serializers.CharField(write_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(MixinUserSerializer.Meta):
        fields = MixinUserSerializer.Meta.fields + ('is_subscribed',)

    def get_is_subscribed(self, obj):
        return False


class UserCreateSerializer(MixinUserSerializer, DjoserUserCreateSerializer):

    class Meta(MixinUserSerializer.Meta):
        pass

    def validate_username(self, value):
        validate_username(value)
        return value


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        read_only_fields = ('id', 'name', 'measurement_unit',)
