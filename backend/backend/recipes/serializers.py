from unicodedata import name
from rest_framework import serializers, status

import webcolors

from .models import Cart, Follow, Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
from users.serializers import UserSerializer
# from users.models import CustomUser
# from users.serializers import CustomUserSerializer


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

class TagSerializer(serializers.ModelSerializer):

    color = ColorFieldSerializer()

    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color')


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
    is_favorited = serializers.SerializerMethodField(source='get_is_favorited')

    class Meta:
        model = Recipe
        fields = ('tags', 'id', 'name', 'author', 'image', 'text',
                 'cooking_time', 'ingredients')

    
    # def get_favorite(self, obj):
    #     return getattr(obj, 'is_favorited', False)

# ----------------------------------------------------------------
class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = IngredientRecipeSerializer(many=True)
    author = UserSerializer(read_only=True)
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

    def get_is_favorited(self, obj):
        print('STEP 3')
        return getattr(obj, 'is_favorited', False)


class CartReadSerializer(serializers.ModelSerializer):

    recipes = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all(), many=True)

    class Meta:
        model = Cart
        fields = ('recipes',)


class CartRecipeWriteSerializer(serializers.ModelSerializer):

    id = serializers.SerializerMethodField(source='cart_recipes')
    name = serializers.SerializerMethodField(source='cart_recipes')
    image = serializers.SerializerMethodField(source='cart_recipes')
    cooking_time = serializers.SerializerMethodField(source='cart_recipes')

    class Meta:
        model = Cart
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_id(self, obj):
        print(obj)
        return obj.cart_recipes.id

    def get_name(self, obj):
        return obj.cart_recipes.name

    def get_image(self, obj):
        return obj.cart_recipes.image

    def get_cooking_time(self, obj):
        return obj.cart_recipes.cooking_time

    def create(self, validated_data):
        user = self.context['request'].user
        recipe = validated_data.pop('recipes')
        cart = Cart.objects.create(**validated_data)
        Recipe.objects.create(user=user, **recipe)
        return cart


# class CartReadSerializer(serializers.ModelSerializer):
#     print(Cart.objects.all())
#     class Meta:
#         model = Cart
#         fields = ('user', 'recipe',)


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
