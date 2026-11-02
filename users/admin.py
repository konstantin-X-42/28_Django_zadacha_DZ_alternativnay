from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """-28- Декоратор настраивает внешний вид таблицы для модели Parent (Родитель) в административной панели Django."""
    list_display = ("id", "email")
