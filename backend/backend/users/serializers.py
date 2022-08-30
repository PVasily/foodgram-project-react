from djoser.serializers import UserCreateSerializer
from recipes.models import Follow
from rest_framework import serializers

from .models import User


class UserSerializer(UserCreateSerializer):

    is_subscribed = serializers.SerializerMethodField(
        source='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = ('username', 'id', 'email', 'first_name',
                  'last_name', 'password', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return getattr(obj, 'is_subscribed', False)


class UserProfileSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'last_name', 'username',
            'first_name', 'email', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Follow.objects.filter(user=request.user, following=obj).exists()
