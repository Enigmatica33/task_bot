from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_id = models.PositiveBigIntegerField(
        unique=True, null=True, blank=True, verbose_name="Telegram ID"
    )

    def __str__(self):
        return f"Пользователь с ID-телеграм {self.telegram_id}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название категории")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Task(models.Model):
    title = models.CharField(
        max_length=120,
        verbose_name="Название задачи"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание задачи"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    due_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Срок выполнения"
    )
    completed = models.BooleanField(default=False)
    category = models.ManyToManyField(Category, verbose_name="Категории")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",
        verbose_name="Автор задачи",
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
