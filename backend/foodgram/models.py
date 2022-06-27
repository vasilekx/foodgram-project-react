from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .validators import validate_tag_color

User = get_user_model()


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=_('Подписчик'),
        help_text=_('Пользователь, который подписывается.'),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Автор'),
        help_text=_('Пользователь, на которого подписываются.'),
    )

    class Meta:
        ordering = ['user']
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='Follow_unique_relationships'),
            models.CheckConstraint(check=~models.Q(user=models.F("author")),
                                   name="prevent_self_follow"),
        ]
    
    def __str__(self):
        return '{} подписан на {}'.format(
            self.user.get_username(),
            self.author.get_username()
        )


class Ingredient(models.Model):
    name = models.CharField(
        _('Название ингредиента'),
        max_length=200,
        db_index=True,
        help_text=_('Используйте общепринятые название ингредиентов.'),
    )
    measurement_unit = models.CharField(
        _('Единица измерения ингредиента'),
        max_length=200,
        help_text=_('Используйте сокращенное обозначения измерений'),
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='Ingredient_unique_relationships'),
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        _('Название тега'),
        max_length=256,
        unique=True,
        help_text=_('Используйте ключевое слово.'),
    )
    color = models.CharField(
        _('Цветовой код тега'),
        max_length=256,
        unique=True,
        validators=[validate_tag_color],
        help_text=_('Следует вводить в виде трёх пар шестнадцатеричных '
                    'цифр с добавлением знака `#` в начале, в виде #123ABC.'),
    )
    slug = models.SlugField(
        _('Короткая метка тега'),
        max_length=50,
        unique=True,
        help_text=_('Укажите короткую метку для тега. Используйте только '
                    'латиницу, цифры, дефисы и знаки подчёркивания')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')

    def __str__(self):
        return f'{self.name}, {self.color}, {self.slug}'


class Recipe(models.Model):
    name = models.CharField(
        _('Название'),
        max_length=256,
        help_text=_('Название рецепта.')
    )
    text = models.TextField(
        _('Описание'),
        help_text=_('Описание рецепта.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор'),
        help_text=_('Автор рецепта.')
    )
    cooking_time = models.IntegerField(
        _('Время приготовления'),
        validators=(MinValueValidator(1),),
        help_text=_('Время приготовления в минутах.')
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        through_fields=('recipe', 'tag')
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient')
    )
    image = models.ImageField(
        _('Картинка'),
        upload_to='foodgram/images/',
        blank=True,
        null=True,
        help_text=_('Изображение готового блюда рецепта.')
    )
    pub_date = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True,
        help_text=_('Дата создания будет автоматически установлена '
                    'в текущую дату при создании рецепта.')
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')

    def __str__(self):
        return '{:.15}'.format(self.name)


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
        null=True,
        help_text=_('Рецепт, к которому будет относиться тег'),
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name=_('Тег'),
        null=True,
        help_text=_('Тег, к которому будет относиться рецепт'),
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = _('Тег рецепта')
        verbose_name_plural = _('Теги рецепта')
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'tag'],
                                    name='RecipeTag_unique_relationships'),
        ]

    def __str__(self):
        return f'У рецепта {self.recipe} есть тег {self.tag}.'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=_('Рецепт'),
        help_text=_('Рецепт, к которому будет относиться ингредиент.'),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=_('Ингредиент'),
        null=True,
        help_text=_('Ингредиент, к которому будет относиться рецепт.'),
    )
    amount = models.IntegerField(
        _('Количество ингредиента'),
        validators=(MinValueValidator(1),),
        help_text=_('Количество ингредиента требуемого для рецепта.')
    )

    class Meta:
        verbose_name = _('Ингредиент рецепта')
        verbose_name_plural = _('Ингредиенты рецепта')
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='RecipeIngredient_unique_relationships')
        ]

    def __str__(self):
        return (f'{self.amount} {self.ingredient.measurement_unit} '
                f'{self.ingredient.name} для рецепта {self.recipe}.')


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Пользователь'),
        help_text=_('Пользователь, у которого будет любимый рецепт')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name=_('Рецепт'),
        help_text=_('Рецепт, который есть у пользователя '
                    'как любимый рецепт.'),
    )

    class Meta:
        ordering = ['user']
        verbose_name = _('Избранный рецепт')
        verbose_name_plural = _('Избранные рецепты')
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='Favorite_unique_relationships')
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у пользователя {self.user}.'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name=_('Пользователь'),
        help_text=_('Пользователь, у которого будет рецепт в списке покупок.')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name=_('Рецепт'),
        help_text=_('Рецепт, который есть у пользователя в списке покупок.'),
    )

    class Meta:
        ordering = ['user']
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзины')
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='ShoppingCart_unique_relationships')
        ]

    def __str__(self):
        return (f'Рецепт {self.recipe} в списке покупок '
                f'у пользователя {self.user}.')
