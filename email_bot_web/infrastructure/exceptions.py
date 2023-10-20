class BotUserAlreadyExists(Exception):
    """Пользователь бота уже существует."""


class BotUserNotFound(Exception):
    """Пользователь бота не найден."""


class BotUserDoesntExist(Exception):
    """Пользователь бота не существует."""


class EmailServiceNotFound(Exception):
    """Почтовый сервис не найден."""


class AvailableServicesNotFound(Exception):
    """Доступные почтовые сервисы не найдены."""


class EmailBoxAlreadyExists(Exception):
    """Почтовый ящик уже существует."""


class EmailBoxNotFound(Exception):
    """Почтовый ящик не найден."""


class UserBoxesNotFound(Exception):
    """Почтовые ящики пользователя не найдены."""


class AppliedFiltersNotFound(Exception):
    """Примененные фильтры не найдены."""


class BoxUserNotEqualToRequestedTelegramUser(Exception):
    """Пользователь почтового ящика не соответствует запрашиваемому пользователю Telegram."""


class EmailCredsInvalid(Exception):
    """Неверные учетные данные электронной почты."""


class IMAPServerTimeout(Exception):
    """Тайм-аут сервера IMAP."""


class IMAPClientIsNotConnected(Exception):
    """Клиент IMAP не подключен."""
