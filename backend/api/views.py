from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.permissions import DenyAll
from api.serializers import UserAvatarSerializer


class UserCustomViewSet(UserViewSet):
    """Кастомынй ViewSet на основе класса библиотеки Djoser."""

    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'update':
            return [DenyAll(),]
        elif (
            self.action == 'me'
            and self.request
            and self.request.method == 'DELETE'
        ):
            return super().get_permissions()
        elif self.action == 'me':
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
