from users.models import User
from rest_framework import serializers, status

import webcolors

import base64

from django.core.files.base import ContentFile

from .models import Cart, Favorite, Follow, Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.serializers import UserProfileSerializer, UserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, basestring) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super(Base64ImageField, self).to_internal_value(data)


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
        fields = ('name', 'measurement_unit', 'id')


class IngredientRecipeSerializer(serializers.ModelSerializer):

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
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        tags = validated_data.get('tags')
        print(validated_data)
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
                'cooking_time': 'Время приготовление должно быть больше нуля!'
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
    ingredients = IngredientRecipeReadSerializer(source='recipe_ing', many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('tags', 'id', 'name', 'author', 'image', 'text',
                 'cooking_time', 'ingredients', 'is_favorited', 'is_in_shopping_cart')

    # def get_is_favorited(self, obj):
    #     return getattr(obj, 'is_favorited', False)

    # def get_is_in_shopping_cart(self, obj):
    #     return getattr(obj, 'is_in_shopping_cart', False)

# -------------- need to test ---------------------
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
    # ---------------------------------------------------


class RecipeForCartAndFavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CartReadSerializer(serializers.ModelSerializer):

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all(), many=True)

    class Meta:
        model = Cart
        fields = ('recipe',)


class CartWriteSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()



    class Meta:
        model = Cart
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_id(self, obj):
        return obj.recipe.id

    def get_name(self, obj):
        return obj.recipe.name

    def get_image(self, obj):
        return obj.recipe.image

    def get_cooking_time(self, obj):
        return obj.recipe.cooking_time

    # def to_representation(self, instance):
    #     repr = super().to_representation(instance)
    #     print(repr)
    #     return repr
        # request = self.context.get('request')
        # context = {'request': request}
        # print(context)
        # return RecipeForCartAndFavoriteSerializer(
        #     instance.recipe, context=context).data

    def create(self, validate_data):
        user = self.context['request'].user
        print(validate_data)
        recipe_id = validate_data.pop('id')
        recipe = Recipe.objects.get(id=recipe_id)
        try:
            if not Cart.objects.get(user=user, recipe=recipe):
                Cart.objects.create(user=user, recipe=recipe)
        except ValueError:
            raise ValueError('Рецепт уже в корзине')


# ------------------FAVORITE-------------------------------------------

class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)

# class FavoriteRecipeSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Favorite
#         fields = ('user', 'recipe', 'is_favorite')


#     def to_representation(self, instance):
#         print(instance)
#         request = self.context.get('request')
#         context = {'request': request}
#         return RecipeForCartAndFavoriteSerializer(
#             instance.recipe, context=context).data

#     def create(self, validated_data):
#         print(validated_data)
#         user = self.context['request'].user
#         recipe = validated_data.pop('id')
#         recipe_in_cart = Favorite.objects.create(user=user, recipes=recipe.id)
#         return recipe_in_cart
# ____________________________________________________________________________

# class CartReadSerializer(serializers.ModelSerializer):
#     print(Cart.objects.all())
#     class Meta:
#         model = Cart
#         fields = ('user', 'recipe',)


class SubcriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class UserSubscrSerializer(UserProfileSerializer):

    class Meta:
        model = User
        fields = ('username', 'id', 'email', 'first_name', 'last_name', 'is_subscribed')


class SubscriptionSerializer(UserSubscrSerializer):
    recipes = SubcriptionRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()


# class SubscriptionGetSerializer(UserSerializer):
#     recipes = serializers.SerializerMethodField(read_only=True)
#     recipes_count = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = User
#         fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

#     def get_recipes(self, obj):
#         return(Recipe.objects.filter(author=obj))

#     def get_recipes_count(self, obj):
#         return (Recipe.objects.filter(author=obj).count())

# class FollowSerializer(serializers.ModelSerializer):

#     user = UserSerializer(read_only=True)
#     author = UserSerializer(read_only=True)
#     recipes = RecipeReadSerializer(queryset=Recipe.objects.filter(author=author))

#     class Meta:
#         model = Follow
#         fields = ('user', 'author', 'recipes')

    # def validate(self, attrs):
    #     print(attrs)
    #     following = self.instanse
    #     follower = self.context.get('request').user
    #     if Follow.objects.filter(following=following, follower=follower):
    #         raise serializers.ValidationError(
    #             detail='Вы уже подписаны на данного пользователя',
    #             code=status.HTTP_400_BAD_REQUEST
    #         )
    #     if follower == following:
    #         raise serializers.ValidationError(
    #             detail='Вы не можете подписаться на самого себя',
    #             code=status.HTTP_400_BAD_REQUEST
    #         )
    #     return attrs
