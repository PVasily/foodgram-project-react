from importlib.metadata import requires
from django.db import models
from django.contrib.auth import get_user_model

from core.validators import cooking_time_validator


User = get_user_model()

CHOICE_UNIT = (
    ('gram', 'г'),
    ('item', 'шт'),
    ('tablespoon', 'ст. л.'),
    ('mililiter', 'мл'),
    ('tea_spoon', 'ч. л.'),
    ('pinch', 'щепотка'),
    ('taste', 'по вкусу')
)

class Ingredient(models.Model):
    name = models.CharField('Название ингредиента', unique=True, max_length=255)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=255,
        choices=CHOICE_UNIT
        )
    amount = models.FloatField('Количество', default=0)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт пользователя."""
    name = models.CharField('Название', blank=True, unique=True, max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField('Изображение', null=True, blank=True, upload_to='recipes/images/')
    text = models.TextField('Описание рецепта', blank=True)
    cooking_time = models.IntegerField(
        'Время приготовления',
        validators=[cooking_time_validator]
        )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
        )
    # ingredients = models.ManyToManyField(
    #     'Ingredient',
    #     related_name='recipe'
    #     )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=255,
        unique=True,
        blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'
