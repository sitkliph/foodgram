import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from api.utils import get_bool_field_value
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для полей изображений в сериализоторах."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='img.' + ext)
        return super().to_internal_value(data)


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для управления полем Avatar модели CustomUser."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения объектов модели CustomUser."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        )

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return get_bool_field_value(user, obj, user.subscriptions)


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


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для поля M:N Ingredients сериализатора Recipe."""

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name', required=False)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', required=False
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name', 'measurement_unit')


class TagsField(serializers.PrimaryKeyRelatedField):
    """
    Кастомное поле, основаное на PrimaryKeyRelatedField.

    Для методов чтения отдаются объекты Tag, для записи принимает id.
    """

    def __init__(self, *args, serializer_class, **kwargs):
        self.serializer_class = serializer_class
        super().__init__(*args, **kwargs)

    def to_representation(self, obj):
        return self.serializer_class(obj, context=self.context).data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор объектов модели Recipe."""

    tags = TagsField(
        many=True,
        queryset=Tag.objects.all(),
        allow_empty=False,
        serializer_class=TagSerializer
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='ingredient_amounts', allow_empty=False
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance is not None:
            self.fields['image'].required = False

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return get_bool_field_value(user, obj, user.favorites)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return get_bool_field_value(user, obj, user.shopping_cart)

    def validate_tags(self, value):
        tags_ids = [tag.id for tag in value]
        if len(tags_ids) != len(set(tags_ids)):
            raise serializers.ValidationError('Теги не должны повторяться.')

        return value

    def validate_ingredients(self, value):
        ingredient_amounts = []
        ingredients_ids = []
        try:
            for ingredient in value:
                ingredients_ids.append(ingredient['ingredient'].get('id'))
                current_ingredient = Ingredient.objects.get(
                    pk=ingredients_ids[-1]
                )
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError(
                'Указан несуществующий ингредиент'
            )
        else:
            ingredient_amounts.append(
                (current_ingredient, ingredient.get('amount'))
            )

        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError('Рецепты не должны повторяться.')

        return ingredient_amounts

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_amounts')
        recipe = Recipe.objects.create(**validated_data)

        ingredient_amounts = []
        for ingredient in ingredients:
            current_ingredient, amount = ingredient
            ingredient_amounts.append(
                IngredientRecipe(
                    ingredient=current_ingredient, recipe=recipe, amount=amount
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_amounts)

        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_amounts')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.tags.set(tags)

        instance.ingredient_amounts.all().delete()
        ingredient_amounts = []
        for ingredient in ingredients:
            current_ingredient, amount = ingredient
            ingredient_amounts.append(
                IngredientRecipe(
                    ingredient=current_ingredient,
                    recipe=instance,
                    amount=amount
                )
            )
        IngredientRecipe.objects.bulk_create(ingredient_amounts)

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


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для визулизации механизма подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()

        if limit:
            recipes = recipes[:int(limit)]

        return RecipeMinifiedSerializer(
            recipes, many=True, context=self.context
        ).data
