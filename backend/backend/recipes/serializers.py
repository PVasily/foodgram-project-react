from dataclasses import fields
from rest_framework import serializers

# from djoser.serializers import UserCreateSerializer, UserProfileSerializer

import webcolors

from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ('username', 'id', 'email', 'first_name', 'last_name', 'password')

class CustomUserCreateSerializer(serializers.ModelSerializer):
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

    # id = serializers.SlugRelatedField(slug_field='id', queryset=Ingredient.objects.all())
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class IRRS(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('name', 'measurement_unit', 'id', 'amount')

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    def get_id(self, obj):
        return obj.ingredient.id


class TagSerializer(serializers.ModelSerializer):

    color = ColorFieldSerializer()

    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color')


# class RecipeCreateSerializer(serializers.ModelSerializer):

#     author = serializers.PrimaryKeyRelatedField(
#         read_only=True,
#         default=serializers.CurrentUserDefault()
#     )
#     tags = serializers.PrimaryKeyRelatedField(
#         queryset=Tag.objects.all(),
#         many=True
#     )
#     ingredients = IngredientRecipeSerializer(many=True)

#     class Meta:
#         model = Recipe
#         fields = '__all__'
   
#     def create(self, validated_data):
#         validated_data['author'] = self.context['request'].user
#         ingredients = validated_data.pop('ingredients')
#         print(ingredients)
#         tags = validated_data.pop('tags')
#         recipe = Recipe.objects.create(**validated_data)
#         for ingredient in ingredients:
#             RecipeIngredient.objects.create(
#                                     # recipe=recipe,
#                                     ingredient=ingredient['id'],
#                                     amount=ingredient['amount'])
#         for tag in tags:
#             RecipeTag.objects.create(recipe=recipe, tag=tag)
#         return recipe


class RecipeReadSerializer(serializers.ModelSerializer):
    
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer()
    ingredients = IRRS(many=True, read_only=True)
    # is_favorited = serializers.SerializerMethodField(source='get_favorite')
    class Meta:
        model = Recipe
        fields = ('tags', 'id', 'name', 'author', 'image', 'text',
                 'cooking_time', 'ingredients')

    
    # def get_favorite(self, obj):
    #     return getattr(obj, 'is_favorited', False)

# ----------------------------------------------------------------
class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    # image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'image',
            'name', 'text', 'tags', 'cooking_time', 'ingredients'
        )

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Выберите ингредиент!'
            })
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': 'Вы уже добавили этот ингредиент!'
                })
            ingredients_list.append(ingredient_id)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError({
                'tags': 'Нужно выбрать хотя бы один тэг!'
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': 'Тэги должны быть уникальными!'
                })
            tags_list.append(tag)

        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовление должно быть больше нуля!'
            })

        return data

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                           recipe=recipe,
                           ingredient=ingredient['id'],
                           amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        author = validated_data.pop('author')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.create_tags(tags, recipe)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        tags = validated_data.get('tags')
        self.create_tags(tags, instance)
        ingredients = validated_data.get('ingredients')
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(
            instance, context=context).data
# -----------------------------------------------------------------


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = '__all__'


# class CartSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Cart
#         fields = ('owner', 'recipes')
