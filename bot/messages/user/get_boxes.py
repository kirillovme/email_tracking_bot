def no_tracking_emails() -> str:
    """Сообщение об отсутствии отслеживаемых адресов."""
    return 'Вы пока что не добавили ни одного адреса для отслеживания 😢'


def choose_email_box() -> str:
    """Сообщение о выборе почтового ящика для изменения."""
    return (
        'На данный момент вы отслеживаете следующие почтовые ящики 🖲\n'
        'Для просмотра информации о ящике - нажмите на адрес электронной почты 👇'
    )


def show_email_box_information(email_box: dict) -> str:
    """Сообщение о выводе информации о почтовом ящике."""
    email_username = email_box.get('email_username', '')
    box_filters = email_box.get('filters', [])
    is_active = email_box.get('is_active', True)
    filters_str = '\n'.join(
        [f"{f['filter_name']} ({f['filter_value']})" for f in box_filters])
    if not filters_str:
        filters_str = 'Нет фильтров'
    status = 'Активный' if is_active else 'Приостановлен'
    return (
        f'Адрес электронной почты: {email_username}\n'
        f'Статус* отслеживания новых сообщений: {status}\n'
        'Применены следующие фильтры:\n'
        f'{filters_str}'
        '\n* Смена статуса происходит в течение минуты ⏰'
    )


def email_box_not_found() -> str:
    """Сообщение об отсутствии почтового ящика."""
    return 'Запрашиваемый почтовый адрес не найден 😢'


def email_deleted() -> str:
    """Сообщение об удалении почтового ящика."""
    return 'Почтовый ящик удален!'
