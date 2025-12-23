from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CategoryViewSet, TaskViewSet, UserViewSet

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('tasks', TaskViewSet, basename='recipes')
v1_router.register('categories', CategoryViewSet, basename='categories')
v1_router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
]
