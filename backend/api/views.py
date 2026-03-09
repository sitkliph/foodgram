from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientSearchFilter, RecipeFilter
from api.permissions import DenyAll, IsAuthorOrAdminOrReadOnly
from api.serializers import (IngredientSerializer, RecipeMinifiedSerializer,
                             RecipeSerializer, SubscriptionSerializer,
                             TagSerializer, UserAvatarSerializer)
from backend.settings import HASHIDS
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class UserCustomViewSet(UserViewSet):
    """Кастомынй ViewSet на основе класса библиотеки Djoser."""

    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'update':
            return [DenyAll(),]
        return super().get_permissions()

    @action(
        ['GET',],
        detail=False,
        permission_classes=[IsAuthenticated,]
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(methods=['PUT', 'DELETE'], detail=False, url_path='me/avatar')
    def avatar(self, request):
        """Action для управления аватаром текущего пользователя."""
        user = request.user
        if request.method == 'PUT':
            serializer = UserAvatarSerializer(user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_200_OK
                )
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = UserAvatarSerializer(user, data={'avatar': None})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET',],
        detail=False,
        permission_classes=[IsAuthenticated,]
    )
    def subscriptions(self, request):
        """Action для получения списка подписок текущего пользователя."""
        subscriptions = User.objects.filter(
            subscribers__user=request.user
        ).annotate(recipes_count=Count('recipes')).order_by('username')
        page = self.paginate_queryset(subscriptions)

        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )

        return self.get_paginated_response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, id=None):
        """Action для добавления и удаления подписок текущего пользователя."""
        author = get_object_or_404(
            User.objects.annotate(recipes_count=Count('recipes')), pk=id
        )
        user = request.user

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            _, created_status = Subscription.objects.get_or_create(
                user=user,
                author=author
            )
            if not created_status:
                return Response(
                    {'errors': 'Вы уже подписаны на данного пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = SubscriptionSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = Subscription.objects.filter(user=user, author=author)
        if not subscription.exists():
            return Response(
                {'errors': 'Вы не подписаны на данного пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    """ViewSet для чтения объектов модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """ViewSet для чтения объектов модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """VeiwSet для работы с эндпоинтами модели Recipe."""

    # TODO Доступна фильтрация по избранному, списку покупок.

    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.prefetch_related(
        Prefetch(
            'ingredient_amounts',
            IngredientRecipe.objects.select_related('ingredient')
        ),
        'tags'
    ).select_related('author')
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    @action(['GET',], detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        """Action для получения короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        code = HASHIDS.encode(recipe.id)
        short_link = request.build_absolute_uri(f'/s/{code}/')

        return Response({'short-link': short_link})

    def service_recipe_options_action(self, request, option_model, pk):
        """Обработчик методов POST, DELETE для корзины покупок и избранного."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            _, created_status = option_model.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            if not created_status:
                return Response(
                    {'errors': 'Рецепт был добавлен ранее'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeMinifiedSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        current_option = option_model.objects.filter(user=user, recipe=recipe)
        if not current_option.exists():
            return Response(
                {'errors': 'Рецепт не добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        current_option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated,]
    )
    def favorite(self, request, pk=None):
        """Action для управления избранными рецептами текущего пользователя."""
        return self.service_recipe_options_action(request, Favorite, pk)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated,]
    )
    def shopping_cart(self, request, pk=None):
        """Action для управления корзиной покупок текущего пользователя."""
        if request.method == 'GET':
            return
        return self.service_recipe_options_action(request, ShoppingCart, pk)

    @action(
        methods=['GET',],
        detail=False,
        permission_classes=[IsAuthenticated,]
    )
    def download_shopping_cart(self, request):
        """Action для скачивания списка покупок пользователя."""
        pass


def redirect_short_link(request, code):
    """Veiw функция для декодирования короткой ссылки на рецепт."""
    try:
        recipe_id = HASHIDS.decode(code)[0]
    except IndexError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return redirect(f'/api/recipes/{recipe_id}/')
