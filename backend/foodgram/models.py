# foodgram/models.py

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .validators import validate_username, validate_tag_color

USER = 'user'
ADMIN = 'admin'

ROLE_CHOICES = (
    (USER, _('Пользователь')),
    (ADMIN, _('Администратор')),
)


class User(AbstractUser):
    username = models.CharField(
        _('Имя пользователя'),
        max_length=150,
        unique=True,
        validators=[validate_username],
    )
    email = models.EmailField(
        _('Адрес электронной почты'),
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        _('Имя'),
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _('Фамилия'),
        max_length=150,
        blank=True,
    )
    role = models.CharField(
        _('Роль'),
        choices=ROLE_CHOICES,
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        default=USER,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=_('Подписчик'),
        help_text=_('Пользователь, который подписывается.'),
        # blank=True,
        # null=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Автор'),
        help_text=_('Пользователь, на которого подписываются.'),
    )

    def __str__(self):
        return '{} followed {}'.format(
            self.user.get_username(),
            self.author.get_username()
        )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_relationships'),
            models.CheckConstraint(check=~models.Q(user=models.F("author")),
                                   name="prevent_self_follow"),
        ]


class Ingredient(models.Model):
    name = models.CharField(
        _('Название ингредиента'),
        max_length=200,
        # unique=True, # не уникальные !!!
    )
    measurement_unit = models.CharField(
        _('Единица измерения ингредиента'),
        max_length=200
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        ordering = ['name']
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_relationships'),
        ]


class Tag(models.Model):
    name = models.CharField(
        _('Название тега'),
        max_length=256,
        unique=True,
    )
    color = models.CharField(
        _('Цветовой код тега'),
        max_length=256,
        unique=True,
        validators=[validate_tag_color],
    )
    slug = models.SlugField(
        _('Короткая метка тега'),
        max_length=50,
        unique=True,
        help_text=_('Укажите короткую метку для тега. Используйте только '
                    'латиницу, цифры, дефисы и знаки подчёркивания')
    )

    def __str__(self):
        return f'{self.name}, {self.color}, {self.slug}'

    class Meta:
        ordering = ['name']
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')


# class Рецепты
class Recipe(models.Model):
    name = models.CharField(
        _('Название'),
        max_length=256,
        help_text=_('Название рецепта')
    )
    text = models.TextField(
        _('Описание'),
        help_text=_('Описание рецепта')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор'),
        help_text=_('Автор, к которому будет относиться рецепт')
    )
    cooking_time = models.IntegerField(
        _('Время приготовления'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(3600)
        ],
        help_text=_('Время приготовления (в минутах)')
    )
    tags = models.ManyToManyField(Tag, through='RecipeTag')
    # image = ...
    # tags = models.ForeignKey(
    #     Tag,
    #     on_delete=models.SET_NULL,
    #     related_name='recipes',
    #     verbose_name=_('Рецепт'),
    #     null=True,
    #     help_text=_('Тег, к которому будет относиться рецепт'),
    # )
    # ingredients = ...

    def __str__(self):
        return '{:.15}'.format(self.name)

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')


# class тег рецепта recipe tag
class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        # related_name='tags',
        verbose_name=_('Рецепт'),
        null=True,
        help_text=_('Рецепт, к которому будет относиться тег'),
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        # related_name='recipes',
        verbose_name=_('Тег'),
        null=True,
        help_text=_('Тег, к которому будет относиться рецепт'),
    )

    def __str__(self):
        return f'{self.recipe} has {self.tag}'

    class Meta:
        verbose_name = _('Тег рецепта')
        verbose_name_plural = _('Теги рецепта')
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'tag'],
                                    name='unique_relationships'),
        ]


# class Ингредиент рецепта  Recipe ingredient
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name=_('Рецепт'),
        help_text=_('Рецепт, к которому будет относиться ингредиент'),
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        related_name='recipes',
        verbose_name=_('Ингредиент'),
        null=True,
        help_text=_('Ингредиент, к которому будет относиться рецепт'),
    )
    amount = models.IntegerField(
        _('Количество'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10000)
        ],
        help_text=_('Количество ингредиента требуемого для рецепта')
    )

    def __str__(self):
        return f'{self.recipe} has {self.ingredient}'

    class Meta:
        verbose_name = _('Ингредиент рецепта')
        verbose_name_plural = _('Ингредиенты рецепта')


# class избранный рецепт  favorite recipe http://127.0.0.1/api/recipes/{id}/favorite/
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
        related_name='users',
        verbose_name=_('Рецепт'),
        help_text=_('Рецепт, который есть у пользователей как любимый рецепт'),
    )

    def __str__(self):
        return f'{self.user} has {self.recipe}'

    class Meta:
        verbose_name = _('Избранный рецепт')
        verbose_name_plural = _('Избранные рецепты')


# class купить рецепт buy recipe shopping cart
class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name=_('Пользователь'),
        help_text=_('Пользователь, у которого будет рецепт в списке покупок')
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppers',
        verbose_name=_('Рецепт'),
        help_text=_('Рецепт, который есть у пользователей в списке покупок'),
    )

    def __str__(self):
        return f'{self.user} has {self.recipe}'

    class Meta:
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзины')
