from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')

urlpatterns = [
    path('me/', views.CurrentUserView.as_view(), name='current_user'),
    path('', include(router.urls)),
]