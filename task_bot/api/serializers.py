from rest_framework import serializers

from bot.models import Category, Task, User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    owner_tg_id = serializers.IntegerField(write_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True
    )

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "due_date",
            "completed",
            "category",
            "user",
            "owner_tg_id",
        ]
        read_only_fields = ["user"]

    def create(self, validated_data):
        tg_id = validated_data.pop("owner_tg_id")
        categories = validated_data.pop("category")
        user, created = User.objects.get_or_create(telegram_id=tg_id)
        task = Task.objects.create(user=user, **validated_data)
        task.category.set(categories)
        return task


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"
