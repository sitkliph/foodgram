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
from api.serializers import (IngredientSerializer, RecipeSerializer,
                             TagSerializer, UserAvatarSerializer)
from backend.settings import HASHIDS
from recipes.models import Ingredient, Recipe, Tag


class UserCustomViewSet(UserViewSet):
    """Кастомынй ViewSet на основе класса библиотеки Djoser."""

    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'update':
            return [DenyAll(),]
        elif (
            self.action == 'me'
            and self.request
            and self.request.method != 'DELETE'
        ):
            return [IsAuthenticated(),]
        return super().get_permissions()

    @action(['GET',], detail=False)
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(methods=['PUT', 'DELETE'], detail=False, url_path='me/avatar')
    def avatar(self, request):
        """View-функция для управления аватаром текущего пользователя."""
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
    queryset = Recipe.objects.all()
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
        """Эндпоинт для получения короткой ссылки на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        code = HASHIDS.encode(recipe.id)
        short_link = request.build_absolute_uri(f'/s/{code}/')

        return Response({'short-link': short_link})


def redirect_short_link(request, code):
    """Veiw функция для декодирования короткой ссылки на рецепт."""
    try:
        recipe_id = HASHIDS.decode(code)[0]
    except IndexError:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return redirect(f'/api/recipes/{recipe_id}/')
