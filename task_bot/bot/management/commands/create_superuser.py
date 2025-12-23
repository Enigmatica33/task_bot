import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Создает суперпользователя из переменных окружения, если его еще нет.
    """

    help = (
        "Creates a superuser from environment variables "
        "if it does not exist"
    )

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not all([username, email, password]):
            self.stdout.write(
                self.style.ERROR(
                    "Переменные окружения DJANGO_SUPERUSER_USERNAME, "
                    "DJANGO_SUPERUSER_EMAIL и DJANGO_SUPERUSER_PASSWORD "
                    "должны быть установлены."
                )
            )
            return

        if not User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f"Создание суперпользователя {username}")
            )
            User.objects.create_superuser(
                username=username, email=email, password=password
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Суперпользователь {username} "
                    "уже существует."
                )
            )
