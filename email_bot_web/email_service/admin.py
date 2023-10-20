from typing import Any

from django.conf import settings
from django.contrib import admin, messages
from django.core.cache import cache
from django.db.models import ProtectedError, QuerySet
from django.forms import ModelForm
from django.http import HttpRequest
from email_service.models import BoxFilter, EmailBox, EmailService
from infrastructure.gateways.imap_client import IMAPStatuses


@admin.register(EmailService)
class EmailServiceAdmin(admin.ModelAdmin):
    """Админ-панель модели почтового сервиса."""

    fields = ('title', 'slug', 'address', 'port')
    list_display = ('id', 'title', 'address')
    list_editable = ('title', 'address')
    search_fields = ('title',)
    search_help_text = 'Поиск по названию'
    ordering = ('title',)
    actions = ['delete_services']
    list_per_page = 50

    def get_actions(self, request: HttpRequest) -> dict[str, Any]:
        """Возвращает список доступных действий для модели. Удаляет стандартное действие "delete_selected"."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request: HttpRequest, obj: EmailService, form: ModelForm, change: bool) -> None:
        """Сохраняет изменения в модели почтового сервиса и очищает кэш."""
        super().save_model(request, obj, form, change)
        cache_keys = [
            settings.EMAIL_SERVICES_KEY_FORMAT,
            settings.EMAIL_SERVICE_KEY_FORMAT.format(service_id=obj.id)
        ]
        cache.delete_many(cache_keys)

    def delete_model(self, request: HttpRequest, obj: EmailService) -> None:
        """Удаляет модель почтового сервиса и очищает кэш, если удаление было успешным."""
        try:
            super().delete_model(request, obj)
            cache_keys = [
                settings.EMAIL_SERVICES_KEY_FORMAT,
                settings.EMAIL_SERVICE_KEY_FORMAT.format(service_id=obj.id)
            ]
            cache.delete_many(cache_keys)
        except ProtectedError:
            self.message_user(
                request,
                'Удаление не удалось: на этот сервис ссылаются некоторые почтовые ящики.',
                messages.ERROR
            )

    def delete_services(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Удаляет выбранные почтовые сервисы."""
        deleted_count = 0
        for obj in queryset:
            try:
                obj.delete()
                deleted_count += 1
                cache_keys = [
                    settings.EMAIL_SERVICES_KEY_FORMAT,
                    settings.EMAIL_SERVICE_KEY_FORMAT.format(service_id=obj.id)
                ]
                cache.delete_many(cache_keys)
            except ProtectedError:
                self.message_user(request, f'Невозможно удалить {obj.title}, так как есть связанные почтовые ящики.',
                                  messages.ERROR)
        if deleted_count:
            self.message_user(request, f'{deleted_count} почтовых сервисов было успешно удалено.', messages.SUCCESS)

    delete_services.short_description = 'Удалить выбранные почтовые сервисы и инвалидировать кэш'  # type: ignore


@admin.register(EmailBox)
class EmailBoxAdmin(admin.ModelAdmin):
    """Админ-панель модели почтового ящика."""

    fields = ('is_active',)
    list_display = ('id', 'user_id', 'email_username', 'email_service', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('user_id',)
    list_filter = ('email_service',)
    actions = ['delete_boxes', 'activate_boxes', 'deactivate_boxes']
    search_help_text = 'Поиск по telegram id пользователя'
    list_per_page = 50

    def get_actions(self, request: HttpRequest) -> dict[str, Any]:
        """Возвращает список доступных действий для модели. Удаляет стандартное действие "delete_selected"."""
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Проверяет, есть ли у пользователя разрешение на добавление объектов модели EmailBox."""
        return False

    def save_model(self, request: HttpRequest, obj: EmailBox, form: ModelForm, change: bool) -> None:
        """Сохраняет изменения в модели почтового ящика и обновляет кэш."""
        if change:
            old_obj = EmailBox.objects.get(id=obj.id)
            if old_obj.is_active != obj.is_active:
                cache_status_key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
                    telegram_id=obj.user_id,
                    box_id=obj.id
                )
                if obj.is_active:
                    cache.set(cache_status_key, IMAPStatuses.ACTIVE.value)
                else:
                    cache.set(cache_status_key, IMAPStatuses.PAUSED.value)
            cache_keys = [
                settings.EMAIL_BOX_KEY_FORMAT.format(box_id=obj.id),
                settings.USER_EMAIL_BOXES_KEY_FORMAT.format(telegram_id=obj.user_id)
            ]
            cache.delete_many(keys=cache_keys)
        super().save_model(request, obj, form, change)

    def delete_model(self, request: HttpRequest, obj: EmailBox) -> None:
        """Удаляет модель почтового ящика и обновляет кэш."""
        cache_status_key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
            telegram_id=obj.user_id,
            box_id=obj.id
        )
        cache.set(cache_status_key, IMAPStatuses.STOPPED.value)
        cache_keys = [
            settings.EMAIL_BOX_KEY_FORMAT.format(box_id=obj.id),
            settings.USER_EMAIL_BOXES_KEY_FORMAT.format(telegram_id=obj.user_id)
        ]
        cache.delete_many(keys=cache_keys)
        super().delete_model(request, obj)

    def delete_boxes(self, request: HttpRequest, queryset: QuerySet[EmailBox]) -> None:
        """Удаляет выбранные ящики и инвалидирует кэш."""
        for obj in queryset:
            cache_status_key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
                telegram_id=obj.user_id,
                box_id=obj.id
            )
            cache.set(cache_status_key, IMAPStatuses.STOPPED.value)
            cache_keys = [
                settings.EMAIL_BOX_KEY_FORMAT.format(box_id=obj.id),
                settings.USER_EMAIL_BOXES_KEY_FORMAT.format(telegram_id=obj.user_id)
            ]
            cache.delete_many(keys=cache_keys)
            obj.delete()
        self.message_user(request, f'{queryset.count()} почтовых ящиков были успешно удалены.', messages.SUCCESS)

    delete_boxes.short_description = 'Удалить почтовые ящики и инвалидировать кэш'  # type: ignore

    def activate_boxes(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Активирует выбранные ящики и инвалидирует кэш.
        """
        for obj in queryset:
            obj.is_active = True
            obj.save()
            cache_status_key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
                telegram_id=obj.user_id,
                box_id=obj.id
            )
            cache.set(cache_status_key, IMAPStatuses.ACTIVE.value)
            cache_keys = [
                settings.EMAIL_BOX_KEY_FORMAT.format(box_id=obj.id),
                settings.USER_EMAIL_BOXES_KEY_FORMAT.format(telegram_id=obj.user_id)
            ]
            cache.delete_many(keys=cache_keys)
        self.message_user(request, f'{queryset.count()} ящиков было успешно активировано.', messages.SUCCESS)

    activate_boxes.short_description = 'Активировать выбранные ящики и инвалидировать кэш'  # type: ignore

    def deactivate_boxes(self, request: HttpRequest, queryset: QuerySet) -> None:
        """
        Деактивирует выбранные ящики и инвалидирует кэш.
        """
        for obj in queryset:
            obj.is_active = False
            obj.save()
            cache_status_key = settings.IMAP_CLIENT_STATUS_KEY_FORMAT.format(
                telegram_id=obj.user_id,
                box_id=obj.id
            )
            cache.set(cache_status_key, IMAPStatuses.PAUSED.value)
            cache_keys = [
                settings.EMAIL_BOX_KEY_FORMAT.format(box_id=obj.id),
                settings.USER_EMAIL_BOXES_KEY_FORMAT.format(telegram_id=obj.user_id)
            ]
            cache.delete_many(keys=cache_keys)
        self.message_user(request, f'{queryset.count()} ящиков было успешно деактивировано.', messages.SUCCESS)

    deactivate_boxes.short_description = 'Деактивировать выбранные ящики и инвалидировать кэш'  # type: ignore


@admin.register(BoxFilter)
class BoxFilterAdmin(admin.ModelAdmin):
    """Админ-панель модели фильтра почтового ящика."""

    list_display = ('id', 'box_id', 'filter_value', 'filter_name')
    list_editable = ('box_id', 'filter_value', 'filter_name')
    search_fields = ('box_id',)
    list_filter = ('box_id',)
    search_help_text = 'Поиск по id почтового ящика'
    list_per_page = 50

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Проверяет, есть ли у пользователя разрешение на добавление объектов модели BoxFilter."""
        return False

    def has_change_permission(self, request: HttpRequest, obj: BoxFilter | None = None) -> bool:
        """Проверяет, есть ли у пользователя разрешение на изменение объектов модели BoxFilter."""
        return False

    def has_delete_permission(self, request: HttpRequest, obj: BoxFilter | None = None):
        """Проверяет, есть ли у пользователя разрешение на удаление объектов модели BoxFilter."""
        return False
