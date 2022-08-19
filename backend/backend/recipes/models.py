from django.db import models

from users.models import User

from core.validators import cooking_time_validator
from users.models import CustomUser


# User = get_user_model()


CHOICE_UNIT = (
    ('gram', 'г'),
    ('item', 'шт'),
    ('tablespoon', 'ст. л.'),
    ('mililiter', 'мл'),
    ('tea_spoon', 'ч. л.'),
    ('pinch', 'щепотка'),
    ('taste', 'по вкусу'),
    ('drop', 'капля')
)


class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', max_length=255)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=255,
        choices=CHOICE_UNIT
        )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=255,
        blank=True)
    slug = models.SlugField()
    color = models.CharField('Цвет', blank=True, max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт пользователя."""
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    name = models.CharField('Название', blank=True, unique=True, max_length=255)
    author = models.ForeignKey(User, related_name='recipes', on_delete=models.CASCADE)
    image = models.ImageField('Изображение', null=True, blank=True, upload_to='recipes/images/')
    text = models.TextField('Описание рецепта', blank=True)
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[cooking_time_validator]
        )
    # ingredients = models.ManyToManyField(
    #     'RecipeIngredient',
    #     related_name='recipe_ingredients',
    #     verbose_name='Ингредиенты',
    #     )
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_cart = models.BooleanField(default=False)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now=True,
        db_index=True)

    def __str__(self):
        return self.name


class RecipeTag(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_ing', on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, related_name='ingredient', on_delete=models.CASCADE)
    amount = models.FloatField('Количество', max_length=10)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='following',
        on_delete=models.CASCADE
    )


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe, related_name='cart_recipes')


# class CartRecipe(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
#     recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
