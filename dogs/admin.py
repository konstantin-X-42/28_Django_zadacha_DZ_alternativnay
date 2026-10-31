from django.contrib import admin
from dogs.models import Dog, Breed, Parent


@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    """-23- Декоратор регистрирует модель Dog в административной панели Django
        и связывает её с классом настроек DogAdmin."""
    list_display = ("id", "name", "breed")
    list_filter = ("breed",)
    search_fields = ("name",)


@admin.register(Breed)
class BreedAdmin(admin.ModelAdmin):
    """-23- Декоратор регистрирует модель Breed (Порода) в административной панели сайта
        и связывает её с классом настроек BreedAdmin."""
    list_display = ("id", "name")


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    """-26- Декоратор настраивает внешний вид таблицы для модели Parent (Родитель) в административной панели Django."""
    list_display = ("id", "name")