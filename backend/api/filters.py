import django_filters
from django_filters.widgets import BooleanWidget
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    """Кастомный фильтр для поиска по названию ингрилиентов."""

    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    """Кастомный фильтр для полей сериализатора Recipe."""

    author = django_filters.CharFilter(field_name='author__id')
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited', widget=BooleanWidget()
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart', widget=BooleanWidget()
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user

        if user.is_authenticated and value:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user

        if user.is_authenticated and value:
            return queryset.filter(recipes_in_shopping_cart__user=user)
        return queryset
