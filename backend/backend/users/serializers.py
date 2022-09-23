from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers, status

from recipes.models import Recipe
from .models import User, Follow


class UserSerializer(UserCreateSerializer):

    is_subscribed = serializers.SerializerMethodField(
        source='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = ('username', 'id', 'email', 'first_name',
                  'last_name', 'password', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context['request'].user,
            author=obj).exists()


class AnonymousUserSerializer(UserCreateSerializer):

    is_subscribed = serializers.SerializerMethodField(
        source='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = ('username', 'id', 'email', 'first_name',
                  'last_name', 'password', 'is_subscribed')

    def get_is_subscribed(self, obj):
        return getattr(obj, 'is_subscribed', False)


class LightsRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class UserGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context['request'].user,
            author=obj).exists()

    def validate(self, attrs):
        following = get_object_or_404(User, email=attrs['email'])
        follower = self.context.get('request').user
        if Follow.objects.filter(user=follower, author=following):
            raise serializers.ValidationError(
                detail='Вы уже подписаны на данного пользователя',
                code=status.HTTP_400_BAD_REQUEST
            )
        if follower == following:
            raise serializers.ValidationError(
                detail='Вы не можете подписаться на самого себя',
                code=status.HTTP_400_BAD_REQUEST
            )
        return attrs


class SubscriptionGetSerializer(UserGetSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()

    def get_recipes(self, obj):
        recipes = Recipe.objects.all()[:3]
        return LightsRecipeSerializer(recipes, many=True, read_only=True).data
