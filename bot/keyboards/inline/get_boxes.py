from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def tracking_emails_keyboard(email_boxes: list) -> InlineKeyboardMarkup:
    """Клавиатура для отображения отслеживаемых почтовых адресов."""
    tracking_emails_kb = InlineKeyboardMarkup(row_width=1)
    for email_box in email_boxes:
        tracking_emails_kb.add(InlineKeyboardButton(
            email_box['email_username'],
            callback_data=f'email_box:{email_box["id"]}'
        ))
    return tracking_emails_kb


def email_box_details_keyboard(email_box: dict) -> InlineKeyboardMarkup:
    """Клавиатура для взаимодействия с определенным почтовым ящиком."""
    details_kb = InlineKeyboardMarkup(row_width=1)
    if email_box['is_active']:
        details_kb.add(InlineKeyboardButton(
            'Приостановить получение новых писем',
            callback_data=f"pause_box:{email_box['id']}"
        ))
    else:
        details_kb.add(InlineKeyboardButton(
            'Возобновить получение новых писем',
            callback_data=f"resume_box:{email_box['id']}"
        ))
    details_kb.add(InlineKeyboardButton(
        'Удалить',
        callback_data=f"delete_box:{email_box['id']}"
    ))
    details_kb.add(InlineKeyboardButton(
        'Назад',
        callback_data='back_to_email_boxes_list'
    ))
    return details_kb


def deletion_status_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для взаимодействия после удаления почтвого ящика."""
    deletion_status_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Назад', callback_data='back_to_email_boxes_list')]
    ])
    return deletion_status_kb
