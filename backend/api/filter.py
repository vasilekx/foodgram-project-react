import django_filters as filters

from foodgram.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__slug', method='tags_filter')
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.NumberFilter(
        method='is_favorited_or_in_shopping_cart_filter'
    )
    is_in_shopping_cart = filters.NumberFilter(
        method='is_favorited_or_in_shopping_cart_filter'
    )

    CASES_VALUES = [1, 0]

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)

    def tags_filter(self, queryset, name, value):
        tags_query_parameter = self.request.query_params.getlist('tags')
        lookup = '__'.join([name, 'in'])
        return queryset.filter(**{lookup: tags_query_parameter}).distinct()

    def is_favorited_or_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated and int(value) in self.CASES_VALUES:
            if name == 'is_favorited':
                queryset = queryset.filter(favorites__user=user)
            if name == 'is_in_shopping_cart':
                queryset = queryset.filter(purchases__user=user)
        return queryset
