from ninja import Schema


class ResponseSchema(Schema):
    """Схема для предоставления информации об ответе с сервера."""
    message: str
