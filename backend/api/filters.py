import django_filters
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

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
