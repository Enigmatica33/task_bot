from django.contrib import admin

from bot.models import Category, Task, User


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ("name", "slug")


class TaskAdmin(admin.ModelAdmin):
    model = Task
    list_display = (
        "id",
        "title",
        "description",
        "created_at",
        "due_date",
        "completed",
        "user",
    )


class UserAdmin(admin.ModelAdmin):
    model = User


admin.site.register(Category, CategoryAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(User, UserAdmin)
