from django.contrib import admin
from .models import Recipe, User, Tag, Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'image', 'text',
                   'cooking_time', 'tags', 'ingredients')
    search_fields = ('name',)
    list_filter = ('author',)

    def ingredients(self, obj):
        return obj.ingredients.all()

    def tags(self, obj):
        return obj.tags.all()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug', 'color')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
