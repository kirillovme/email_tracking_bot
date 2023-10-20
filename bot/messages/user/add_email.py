def no_available_services() -> str:
    """Сообщение, которое выводится при отсутствии доступных сервисов."""
    return 'На данный момент доступные сервисы отсутствуют 🥶'


def choose_email_service() -> str:
    """Сообщение выбора почтового сервиса."""
    return '1️⃣ Выберите ваш почтовый сервис из списка ниже.'


def add_email_box() -> str:
    """Сообщение о вводе электронной почты."""
    return '2️⃣ Введите вашу электронную почту в формате example@gmail.com.'


def add_email_password() -> str:
    """Сообщение о вводе пароля от почтового ящика."""
    return '3️⃣ Введите пароль от вашей электронной почты.'


def add_email_filter_value() -> str:
    """Сообщение о добавлении значения фильтра."""
    return (
        'Ваш пароль был скрыт в целях безопасности 🛡\n'
        '4️⃣ Введите почтовый адрес, с которого хотите получать письма\n'
        'Формат: example@gmail.com'
    )


def add_next_email_filter_value() -> str:
    """Сообщение о добавлении следующего значения фильтра"""
    return (
        '4️⃣ Введите следующий почтовый адрес, с которого хотите получать письма\n'
        'Формат: example@gmail.com'
    )


def add_email_filter_name() -> str:
    """Сообщение о добавлении названия фильтра."""
    return '5️⃣ Пожалуйста, придумайте название для данного почтового адреса:'


def filter_reminder_instruction() -> str:
    """Сообщение, которое напоминает о функционале фильтрации."""
    return '⚠️Бот будет отправлять вам письма только с перечисленных вами адресов!⚠️'


def more_filters_question() -> str:
    """Сообщение, которое уточняет необходимость добавления дополнительных фильтров."""
    return 'Вы хотите добавить еще почтовые адреса для отслеживания?🤔'


def add_email_box_instruction() -> str:
    """Сообщение, которое отправляется при начале добавления почтового ящика."""
    return (
        '📬 Здесь вы сможете добавить свой почтовый ящик на отслеживание.\n'
        'Я пошагово проведу вас через данный процесс! 🤖\n'
        'В случае, если у вас включена двухфакторная аутентификация (2FA), следует создать пароль для приложения, '
        'чтобы я мог получить доступ к почтовому ящику. Вот как это можно сделать:\n'
        '1. Войдите в свою учетную запись электронной почты. 📧\n'
        '2. Перейдите в раздел "Безопасность" или аналогичный раздел в настройках учетной записи. ⚙️\n'
        '3. Найдите опцию "Пароли приложений" или что-то подобное и создайте новый пароль для бота. 🔑\n'
        '4. Введите этот пароль при добавлении почтового ящика в бота. ➕\n'
        'Будьте внимательны и следуйте инструкциям вашего почтового провайдера для создания пароля приложения. 🧐\n'
    )


def incorrect_email_address() -> str:
    """Сообщение, которое отправляется при вводе невалидного почтового адреса"""
    return (
        'Мне неизвестны почтовые ящики в таком формате🧐\n'
        'Проверьте правильность ввода и попробуйте еще раз.'
    )


def incorrect_email_creds() -> str:
    """Сообщение, которое отправляется в случае невалидных кредов."""
    return 'Вы неправильно ввели логин или пароль от почты. Попробуйте еще раз!'


def email_box_created() -> str:
    """Сообщение, которое добавляется, когда почттовый ящик создан."""
    return 'Почтовый ящик успешно создан!💥'
