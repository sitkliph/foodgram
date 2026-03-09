from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from backend.constants import (CHARS_LIMIT, INGREDIENT_MEASUREMENT_UNIT_LENGTH,
                               INGREDIENT_NAME_LENGTH, RECIPE_NAME_LENGTH,
                               SLUG_LENGTH, TAG_NAME_LENGTH)

User = get_user_model()


class BaseAbstractModel(models.Model):
    """
    Базовая абстрактная модель для моделей приложения.

    В модели выполнены:
    - Сортировка объектов моделей по полю name.
    - Текстовое представление формируется полем name.
    """
    class Meta:
        abstract = True
        ordering = ['name',]

    def __str__(self):
        return self.name[:CHARS_LIMIT]


class Tag (BaseAbstractModel):
    """Модель Тэг для маркировки рецептов по тематическим категориям."""

    name = models.CharField('Наименование', max_length=TAG_NAME_LENGTH)
    slug = models.SlugField('Идентификатор', max_length=SLUG_LENGTH)

    class Meta(BaseAbstractModel.Meta):
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'


class Ingredient(BaseAbstractModel):
    """Модель Ингридиент для формирования состава рецептов."""

    name = models.CharField('Наименование', max_length=INGREDIENT_NAME_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=INGREDIENT_MEASUREMENT_UNIT_LENGTH
    )

    class Meta(BaseAbstractModel.Meta):
        verbose_name = 'ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return super().__str__() + f', {self.measurement_unit}'


class Recipe(BaseAbstractModel):
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
        validators=[MinValueValidator(1),]
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe', verbose_name='Ингридиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Тэги')

    class Meta(BaseAbstractModel.Meta):
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class IngredientRecipe(models.Model):
    """
    Промежуточная модель для поля Ингридиенты типа N:M в модели Рецепт.

    В модели указано дополнительное поле для количества ингридиента Amount.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredient_amounts'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингридиент'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1),],
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

    def __str__(self):
        return f'Состав рецепта {self.recipe.name[:CHARS_LIMIT]}:'
