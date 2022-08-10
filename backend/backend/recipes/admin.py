from django.contrib import admin
from .models import Recipe, User, Tag, Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'image', 'text', 'cooking_time', 'ingredients')
    search_fields = ('name',)
    list_filter = ('author',)

    def ingredients(self, obj):
        return obj.ingredients_set.all()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit', 'amount')
