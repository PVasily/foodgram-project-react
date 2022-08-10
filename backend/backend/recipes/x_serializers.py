from xml.etree.ElementInclude import include
from rest_framework import serializers

import webcolors

from .models import Ingredient, Recipe, Tag, User, RecipeIngredient


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'id', 'email', 'first_name', 'last_name', )


class ColorFieldSerializer(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Нет цвета с таким именем')
        return data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientToRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        print(obj.amount)


class TagSerializer(serializers.ModelSerializer):

    color = ColorFieldSerializer()

    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color')


class RecipeCreateSerializer(serializers.ModelSerializer):
    # ingredients = serializers.SlugRelatedField(
    #     slug_field='slug',
    #     queryset=Ingredient.objects.all(),
    #     many=True
    # )
    ingredients = IngredientToRecipeSerializer(many=True)
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset = User.objects.all()
        )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'image', 'text',
                 'cooking_time', 'ingredients')

    def create(self, validated_data):
        data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in data:
            current_data, _ = Ingredient.objects.get_or_create(**ingredient)
            RecipeIngredient.objects.create(recipe=recipe, ingredient=current_data)
        return recipe


class RecipeReadSerializer(serializers.ModelSerializer):
    
    author = UserSerializer()
    ingredients = IngredientSerializer(many=True, read_only=True)
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'image', 'text',
                 'cooking_time', 'ingredients')