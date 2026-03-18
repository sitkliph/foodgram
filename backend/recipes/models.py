from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from backend.constants import (CHARS_LIMIT, INGREDIENT_MEASUREMENT_UNIT_LENGTH,
                               INGREDIENT_NAME_LENGTH, MIN_COOKING_TIME,
                               MIN_INGREDIENT_AMOUNT, RECIPE_NAME_LENGTH,
                               SLUG_LENGTH, TAG_NAME_LENGTH)

User = get_user_model()


class Tag (models.Model):
    """Модель Тэг для маркировки рецептов по тематическим категориям."""

    name = models.CharField('Наименование', max_length=TAG_NAME_LENGTH)
    slug = models.SlugField(
        'Идентификатор', max_length=SLUG_LENGTH, db_index=True
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['name', ]

    def __str__(self):
        return self.name[:CHARS_LIMIT]


class Ingredient(models.Model):
    """Модель Ингридиент для формирования состава рецептов."""

    name = models.CharField(
        'Наименование', max_length=INGREDIENT_NAME_LENGTH, db_index=True
    )
    measurement_unit = models.CharField(
        'Единица измерения', max_length=INGREDIENT_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_object'
            )
        ]
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'
        ordering = ['name', ]

    def __str__(self):
        return super().__str__() + f', {self.measurement_unit}'


class Recipe(models.Model):
    """Модель Рецепт для публикаций рецептов пользвоателями."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField('Название', max_length=RECIPE_NAME_LENGTH)
    image = models.ImageField('Картинка', upload_to='recipes/images/')
    text = models.TextField('Описание')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[MinValueValidator(MIN_COOKING_TIME), ]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe', verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['name', ]

    def __str__(self):
        return self.name[:CHARS_LIMIT]


class IngredientRecipe(models.Model):
    """
    Промежуточная модель для поля Ингридиенты типа N:M в модели Рецепт.

    В модели указано дополнительное поле для количества ингридиента Amount.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT), ],
        verbose_name='Количество'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_per_recipe'
            )
        ]
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'
        default_related_name = 'ingredient_amounts'

    def __str__(self):
        return f'Состав рецепта {self.recipe.name[:CHARS_LIMIT]}:'


class RecipeOptionsAbsractModel(models.Model):
    """Абстрактная модель для расширений модели Recipe."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('user__username',)


class Favorite(RecipeOptionsAbsractModel):
    """Модель избранных рецептов пользователей."""

    class Meta(RecipeOptionsAbsractModel.Meta):
        default_related_name = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name[:CHARS_LIMIT]} в избранном у '
            f'пользователя {self.user.username}'
        )


class ShoppingCart(RecipeOptionsAbsractModel):
    """Модель корзины покупок пользователей."""

    class Meta(RecipeOptionsAbsractModel.Meta):
        default_related_name = 'recipes_in_shopping_cart'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_cart'
            )
        ]
        verbose_name = 'корзина покупок'
        verbose_name_plural = 'Корзины покупок'

    def __str__(self):
        return (
            f'Рецепт {self.recipe.name[:CHARS_LIMIT]} в списке покупок '
            f'пользователя {self.user.username}'
        )
