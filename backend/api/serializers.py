# api/serialiser.py

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from foodgram.models import User
from foodgram.validators import validate_username


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'password',
            'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_username(self, value):
        validate_username(value)
        return value

    def get_is_subscribed(self, obj):
        return False


class MeUserSerializer(UserSerializer):
    pass
