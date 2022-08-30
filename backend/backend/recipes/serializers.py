import webcolors
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from users.models import User
from users.serializers import UserSerializer

from .models import (Cart, Favorite, Follow, Ingredient, Recipe,
                     RecipeIngredient, Tag)


class ColorFieldSerializer(serializers.Field):

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            return webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Нет цвета с таким именем')


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
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'name', 'author', 'image',
                  'text', 'cooking_time', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart')

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        print(instance)
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
                'cooking_time': 'Время приготовление должно быть больше нуля'
            })

        return data


class IngredientRecipeReadSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeReadSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer()
    ingredients = IngredientRecipeReadSerializer(
        source='recipe_ing', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('tags', 'id', 'name', 'author', 'image', 'text',
                  'cooking_time', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        favorite = Favorite.objects.filter(
            user=user, recipe=obj
        )
        return favorite.exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        recipe_in_cart = Cart.objects.filter(
            user=user, recipe=obj
        )
        return recipe_in_cart.exists()


class LightRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionSerializer(UserSerializer):
    recipes = LightRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class UserGetSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=self.context['request'].user,
            author=obj).exists()


class SubscriptionGetSerializer(UserGetSerializer):
    recipes = LightRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(UserGetSerializer.Meta):
        fields = UserGetSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, obj):
        return (Recipe.objects.filter(author=obj))

    def get_recipes_count(self, obj):
        return (Recipe.objects.filter(author=obj).count())

    def validate(self, attrs):
        following = User.objects.get(email=attrs['email'])
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


# ------------------------------------------------------------------------
    # is_subscribed = serializers.SerializerMethodField()

    # def get_is_subscribed(self, obj):
    #     user = self.context['request'].user
    #     if user.is_anonymous:
    #         return False
    #     is_subscribe = Follow.objects.filter(
    #         user=user, author=obj
    #     )
    #     return is_subscribe.exists()

    # class IRRS(serializers.ModelSerializer):
#     name = serializers.SerializerMethodField()
#     measurement_unit = serializers.SerializerMethodField()
#     id = serializers.SerializerMethodField()

#     class Meta:
#         model = RecipeIngredient
#         fields = ('name', 'measurement_unit', 'id', 'amount')

#     def get_name(self, obj):
#         return obj.ingredient.name

#     def get_measurement_unit(self, obj):
#         return obj.ingredient.measurement_unit

#     def get_id(self, obj):
#         return obj.ingredient.id


# def get_is_favorited(self, obj):
    #     print(self.context)
    #     return getattr(obj, 'is_favorited', False)

    # def get_is_in_shopping_cart(self, obj):
    #     return getattr(obj, 'is_in_shopping_cart', False)

# -------------- need to test ---------------------
