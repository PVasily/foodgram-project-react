from django.contrib import admin
from .models import (Favorite, Recipe, RecipeIngredient,
                     RecipeTag, Tag, Ingredient)


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient


class RecipeTagAdmin(admin.TabularInline):
    model = RecipeTag


class QtyIsFavoritedRecipe(admin.TabularInline):
    model = Favorite
    fields = ('qty',)
    readonly_fields = ('qty',)
    verbose_name_plural = 'Общее количество добавлений в Избранное'
    can_delete = False

    def qty(self, obj):
        recipe = Recipe.objects.get(name=obj)
        qty = recipe.favorite_recipes.filter(recipe=recipe).count()
        return qty


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    inlines = [RecipeIngredientAdmin, RecipeTagAdmin, QtyIsFavoritedRecipe]

    def ingredients(self, obj):
        print(obj)
        return obj.recipe_ing.all()

    def tags(self, obj):
        return obj.tags.all()


class RecipeIngredients(admin.TabularInline):
    model = Recipe.recipe_ing
    print(Recipe.recipe_ing)


class IngredentsInline(admin.TabularInline):
    model = Recipe
    inlines = [RecipeIngredients]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name', )
