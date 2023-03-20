from django.urls import include, path
from rest_framework import routers

from api.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                    ReviewViewSet, TitleViewSet)
from users.views import UserViewSet, create_token, create_user



v1_router = routers.DefaultRouter()
v1_router.register('users', UserViewSet)
v1_router.register(r'categories', CategoryViewSet, basename='categories')
v1_router.register(r'genres', GenreViewSet, basename='genres')
v1_router.register(r'titles', TitleViewSet, basename='titles')
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="review"
)
v1_router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename='comment',
)


urlpatterns = [
    path('v1/auth/signup/', create_user),
    path('v1/auth/token/', create_token),
    path('v1/', include(v1_router.urls)),
]
