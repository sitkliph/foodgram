from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UserCustomViewSet)

router_v1 = SimpleRouter()
router_v1.register('users', UserCustomViewSet)
router_v1.register('tags', TagViewSet)
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('recipes', RecipeViewSet)
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet,
#     basename='reviews'
# )
# router_v1.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments'
# )

api_v1_patterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('', include(api_v1_patterns)),
]
