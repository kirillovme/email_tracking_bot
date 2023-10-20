from django.contrib import admin
from django.http import HttpRequest
from user.models import BotUser


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    """Админ панель модели пользователя."""

    fields = ('telegram_id',)
    list_display = ('telegram_id',)
    search_fields = ('telegram_id',)
    ordering = ('telegram_id',)
    search_help_text = 'Поиск по telegram ID'
    list_per_page = 50

    def has_change_permission(self, request: HttpRequest, obj: BotUser | None = None) -> bool:
        """Проверяет, есть ли у пользователя разрешение на изменение объектов модели BotUser."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: BotUser | None = None) -> bool:
        """Проверяет, есть ли у пользователя разрешение на удаление объектов модели BotUser."""
        return False

    def has_add_permission(self, request: HttpRequest):
        """Проверяет, есть ли у пользователя разрешение на добавление объектов модели BotUser."""
        return False
