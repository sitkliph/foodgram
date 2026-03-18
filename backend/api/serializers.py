from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag

User = get_user_model()


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для управления полем Avatar модели CustomUser."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserReadSerializer(UserSerializer):
    """Сериализатор для чтения объектов модели CustomUser."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields
        fields += (
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user

        return (
            user.is_authenticated
            and user.subscriptions.filter(author=obj).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeListSerializer(serializers.ListSerializer):
    """Сериализатор списка для сериализатора IngredientRecipeSerializer."""

    def validate(self, data):
        ingredient_ids = [item['ingredient'].id for item in data]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return data


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для поля M:N Ingredients сериализатора Recipe."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', required=False
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name', 'measurement_unit')
        list_serializer_class = IngredientRecipeListSerializer


class RecipeBaseSerializer(serializers.ModelSerializer):
    """Базовый класс для сериализаторов модели Recipe."""

    author = UserReadSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredient_amounts', allow_empty=False
    )

    class Meta:
        model = Recipe


class RecipeReadSerializer(RecipeBaseSerializer):
    """Сериализатор для чтения объектов модели Recipe."""

    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta(RecipeBaseSerializer.Meta):
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user

        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user

        return (
            user.is_authenticated
            and user.recipes_in_shopping_cart.filter(recipe=obj).exists()
        )


class RecipeWriteSerializer(RecipeBaseSerializer):
    """Сериализатор для записи объектов модели Recipe."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), allow_empty=False
    )
    image = Base64ImageField()

    class Meta(RecipeBaseSerializer.Meta):
        fields = '__all__'

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    def validate_image(self, value):
        if value == '' or value is None:
            raise serializers.ValidationError('Пустое значение.')
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request.method == 'PATCH':
            required_fields = [
                'ingredient_amounts', 'tags', 'name', 'text', 'cooking_time'
            ]
            for field in required_fields:
                if field not in data:
                    raise serializers.ValidationError(
                        {field: 'Не заполнено обязательное поле.'}
                    )

        tags = data.get('tags')
        if tags and len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться.'}
            )
        return data

    def create_ingredients(self, recipe: Recipe, ingredients: dict) -> None:
        """Метод для создания инглидиентов в модели Recipe."""
        ingredient_amounts = [
            IngredientRecipe(
                ingredient=ingredient.get('ingredient'),
                recipe=recipe,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        ]
        IngredientRecipe.objects.bulk_create(ingredient_amounts)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_amounts')
        recipe = Recipe.objects.create(**validated_data)

        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_amounts')

        super().update(instance, validated_data)

        instance.tags.set(tags)
        instance.ingredient_amounts.all().delete()
        self.create_ingredients(instance, ingredients)

        return instance


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для чтения объектов модели Recipe."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(UserReadSerializer):
    """Сериализатор для визулизации механизма подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(UserReadSerializer.Meta):
        fields = UserReadSerializer.Meta.fields
        fields += (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()

        if limit:
            try:
                limit = int(limit)
            except ValueError:
                raise serializers.ValidationError({
                    'recipes_limit': 'Значение должно быть целым числом.'
                })
            recipes = recipes[:limit]

        return RecipeMinifiedSerializer(
            recipes, many=True, context=self.context
        ).data
