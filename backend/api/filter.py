# api/filter.py

import django_filters as filters

from foodgram.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__slug')
    author = filters.NumberFilter(field_name='author__id')
    test = filters.BooleanFilter(method='test_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'test',)

    def test_filter(self, queryset, name, value):
        s = self
        q = queryset
        n = name
        v = value
        return queryset