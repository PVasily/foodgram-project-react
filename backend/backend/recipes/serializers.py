from rest_framework import serializers


import webcolors

from .models import Amount, Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag, User


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

# -------------------- Ingredients--------------------------------

class IngredientReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit', 'id')


class IngredientSerializer(serializers.ModelSerializer):

    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ['name', 'measurement_unit', 'amount']

    def get_amount(self, obj):
        if type(obj.amount) == float:
            return obj.amount
        return str(obj.amount)


# class IngredientToRecipeSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Ingredient
#         fields = ['name', 'measurement_unit', 'amount']

# class AmountSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Amount
#         fields = ('amount',)


class IngredientToRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['name', 'measurement_unit', 'amount']

# -----------------------------------------------------------------------
# ------------------------ Tags -----------------------------------------

class TagSerializer(serializers.ModelSerializer):

    color = ColorFieldSerializer()

    class Meta:
        model = Tag
        fields = ('name', 'slug', 'color')

# --------------------------------------------------------------------------

class RecipeCreateSerializer(serializers.ModelSerializer):
    # ingredients = serializers.SlugRelatedField(
    #     slug_field='name',
    #     queryset=Ingredient.objects.all(),
    #     many=True
    # )

    # tags = serializers.SlugRelatedField(
    #     slug_field='slug',
    #     queryset=Tag.objects.all(),
    #     many=True
    # )
    tags = TagSerializer(many=True)
    ingredients = IngredientToRecipeSerializer(many=True)
    # author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('tags', 'id', 'name', 'author', 'image', 'text',
                 'cooking_time', 'ingredients')

   
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        # amount = ingredients[0]['recipeingredient']['amount']
        # amount = ('amount', amount)
        # ingredients = ingredients[0]
        # print(ingredients)
        
        tags = validated_data.pop('tags')
        
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            print(ingredient)
            current_ingrd, status = Ingredient.objects.get_or_create(**ingredient)
            RecipeIngredient.objects.create(recipe=recipe, ingredient=current_ingrd)
        for tag in tags:
            current_tag, status = Tag.objects.get_or_create(**tag)
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        return recipe

         # def create(self, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)
    #     for ingredient in ingredients:
    #         print(ingredient)
    #         current_data, status = Ingredient.objects.get_or_create(**ingredient)
    #         RecipeIngredient.objects.create(recipe=recipe, ingredient=current_data)
    #     for tag in tags:
    #         current_tag, status = Tag.objects.get_or_create(**tag)
    #         RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        # return recipe


class RecipeReadSerializer(serializers.ModelSerializer):
    
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer()
    ingredients = IngredientSerializer(many=True, read_only=True)
    class Meta:
        model = Recipe
        fields = ('tags', 'id', 'name', 'author', 'image', 'text',
                 'cooking_time', 'ingredients')


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


# class CartSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Cart
#         fields = ('owner', 'recipes')
