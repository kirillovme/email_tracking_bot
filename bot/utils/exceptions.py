class BotUserNotFound(Exception):
    """Пользователь бота не найден."""


class APIInternalError(Exception):
    """API недоступно."""


class BotUserAlreadyExists(Exception):
    """Пользователь бота уже существует."""


class EmailCredsInvalid(Exception):
    """Неверные учетные данные электронной почты."""


class AvailableServicesNotFound(Exception):
    """Доступные почтовые сервисы не найдены."""


class UserBoxesNotFound(Exception):
    """Почтовые ящики пользователя не найдены."""


class EmailBoxNotFound(Exception):
    """Почтовый ящик не найден."""
