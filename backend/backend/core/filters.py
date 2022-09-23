from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilterMainPage(filters.FilterSet):

    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )


class TagsFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    def get_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(
                favorite_recipes__user=self.request.user
            )
        return queryset.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                cart_recipes__user=self.request.user
            )
        return queryset.all()

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains', )

    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')
