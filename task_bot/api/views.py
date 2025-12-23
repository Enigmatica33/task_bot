from rest_framework import viewsets

from api.serializers import CategorySerializer, TaskSerializer, UserSerializer
from bot.models import Category, Task, User


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Фильтрует задачи на основе параметра 'owner_tg_id',
        переданного в URL.
        """
        telegram_id = self.request.query_params.get('owner_tg_id')
        if telegram_id:
            return Task.objects.filter(user__telegram_id=telegram_id)
        return Task.objects.none()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get", "post", "put", "delete"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ["get"]
