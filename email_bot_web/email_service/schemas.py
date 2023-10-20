from email_service.models import BoxFilter, EmailBox, EmailService
from ninja import ModelSchema, Schema


class EmailBoxSchema(ModelSchema):
    """Схема для почтового ящика."""

    class Config:
        model = EmailBox
        model_fields = ['email_service', 'email_username', 'email_password']


class BoxFilterSchema(ModelSchema):
    """Схема для фильтра почтового ящика."""

    class Config:
        model = BoxFilter
        model_fields = ['filter_value', 'filter_name']


class EmailServiceSchema(ModelSchema):
    """Схема для почтового сервиса."""

    class Config:
        model = EmailService
        model_fields = ['id', 'title']


class EmailBoxIn(EmailBoxSchema):
    """Схема для входящего почтового ящика."""

    filters: list[BoxFilterSchema]


class EmailBoxOut(ModelSchema):
    """Схема для вывода почтового ящика без фильтров."""

    class Config:
        model = EmailBox
        model_fields = ['id', 'email_service', 'email_username', 'is_active']


class EmailBoxWithFiltersOut(EmailBoxOut):
    """Схема для вывода почтового ящика с фильтрами."""

    filters: list[BoxFilterSchema]


class EmailBoxesOut(Schema):
    """Схема для вывода данных о почтовых ящиках пользователя."""

    email_boxes: list[EmailBoxOut]


class BoxFiltersOut(Schema):
    """Схема для вывода данных о фильтрах почтового ящика."""

    filters: list[BoxFilterSchema]


class EmailServicesList(Schema):
    """Схема для вывода данных о поддерживаемых сервисах."""

    services: list[EmailServiceSchema]
