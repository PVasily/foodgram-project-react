from django.contrib import admin
from .models import Favorite, Recipe, Tag, Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'image', 'text',
                   'cooking_time', 'tags', 'ingredients')
    search_fields = ('name',)
    list_filter = ('author',)


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
