from django.contrib import admin
from admin_decorators import short_description

from .models import (
    Cart, Favorite, Ingredient, Recipe,
    RecipeIngredient, RecipeTag, Tag
)


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient


class RecipeTagAdmin(admin.TabularInline):
    model = RecipeTag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'in_favorited')
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags')
    inlines = [RecipeIngredientAdmin, RecipeTagAdmin]

    @short_description('Количество добавлений в Избранное')
    def in_favorited(self, obj):
        return Recipe.objects.filter(favorite_recipes__recipe=obj).count()

    def ingredients(self, obj):
        return obj.recipe_ing.all()

    def tags(self, obj):
        return obj.tags.all()


class RecipeIngredients(admin.TabularInline):
    model = Recipe.recipe_ing


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


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
