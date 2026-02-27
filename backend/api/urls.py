from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import UserCustomViewSet

router_v1 = SimpleRouter()
router_v1.register('users', UserCustomViewSet)
# router_v1.register('categories', CategoryViewSet, basename='categories')
# router_v1.register('genres', GenreViewSet, basename='genres')
# router_v1.register('titles', TitleViewSet, basename='titles')
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
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path('', include(api_v1_patterns)),
]
