from rest_framework import serializers

from djoser.serializers import UserCreateSerializer

import webcolors

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import CustomUser


class CustomUserSerializer(UserCreateSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'id', 'email', 'first_name', 'last_name', 'password', 'is_subscribed')

class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'email',
            'username',
            'password'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class ColorFieldSerializer(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Нет цвета с таким именем')
        return data

# -------------------- Ingredients--------------------------------

class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'id')


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):

    color = ColorFieldSerializer()

    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color')


class RecipeCreateSerializer(serializers.ModelSerializer):

    author = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'
   
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                                    recipe=recipe,
                                    ingredient=ingredient['id'],
                                    amount=ingredient['amount'])
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        return recipe


class RecipeReadSerializer(serializers.ModelSerializer):
    
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer()
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField(source='get_favorite')
    class Meta:
        model = Recipe
        fields = ('tags', 'id', 'name', 'author', 'image', 'text',
                 'cooking_time', 'ingredients', 'is_favorited')

    @staticmethod
    def get_favorite(obj):
        return getattr(obj, 'is_favorited', False)


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'


# class CartSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Cart
#         fields = ('owner', 'recipes')
