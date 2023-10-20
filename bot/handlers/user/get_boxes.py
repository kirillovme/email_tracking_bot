from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config.config import API_ERROR
from keyboards.inline import get_boxes as get_boxes_kb
from keyboards.reply import user_reply as user_reply_kb
from messages.user import get_boxes as get_boxes_mg
from utils.api_client import APIClient
from utils.exceptions import APIInternalError, EmailBoxNotFound, UserBoxesNotFound


async def handle_get_boxes(message: types.Message, state: FSMContext, api: APIClient) -> None:
    """Хендлер сообщения о выводе отслеживаемых почтовых ящиках."""
    email_boxes = await api.get_user_boxes(message.from_user.id)
    if not email_boxes.error and email_boxes.data:
        await message.answer(
            text=get_boxes_mg.choose_email_box(),
            reply_markup=get_boxes_kb.tracking_emails_keyboard(email_boxes.data)
        )
    elif email_boxes.error is UserBoxesNotFound:
        await message.answer(get_boxes_mg.no_tracking_emails(), reply_markup=user_reply_kb.bot_main_keyboard())
    elif email_boxes.error is APIInternalError:
        await message.answer(
            text=API_ERROR
        )


async def handle_get_box(query: types.CallbackQuery, state: FSMContext, api: APIClient) -> None:
    """Хендлер сообщения о выводе информации о конкретном почтовом ящике."""
    box_id = int(query.data.split(':')[1])
    email_box = await api.get_user_box(query.from_user.id, box_id)
    if not email_box.error and email_box.data:
        await query.message.edit_text(
            get_boxes_mg.show_email_box_information(email_box.data),
            reply_markup=get_boxes_kb.email_box_details_keyboard(email_box.data)
        )
    elif email_box.error is EmailBoxNotFound:
        await query.message.edit_text(get_boxes_mg.email_box_not_found())
    elif email_box.error is APIInternalError:
        await query.message.answer(
            text=API_ERROR
        )
        await query.message.delete()


async def handle_pause_box(query: types.CallbackQuery, state: FSMContext, api: APIClient) -> None:
    """Хендлер приостановки отслеживания почтового ящика."""
    box_id = int(query.data.split(':')[1])
    pause_response = await api.pause_box(query.from_user.id, box_id)
    if not pause_response.error:
        email_box = await api.get_user_box(query.from_user.id, box_id)
        if not email_box.error and email_box.data:
            await query.message.edit_text(
                get_boxes_mg.show_email_box_information(email_box.data),
                reply_markup=get_boxes_kb.email_box_details_keyboard(email_box.data)
            )
        elif email_box.error is EmailBoxNotFound:
            await query.message.edit_text(get_boxes_mg.email_box_not_found())
        elif email_box.error is APIInternalError:
            await query.message.answer(
                text=API_ERROR
            )
            await query.message.delete()
    elif pause_response.error is EmailBoxNotFound:
        await query.message.edit_text(get_boxes_mg.email_box_not_found())
    elif pause_response.error is APIInternalError:
        await query.message.answer(
            text=API_ERROR
        )
        await query.message.delete()


async def handle_resume_box(query: types.CallbackQuery, state: FSMContext, api: APIClient) -> None:
    """Хендлер возобновления отслеживания почтового ящика."""
    box_id = int(query.data.split(':')[1])
    resume_response = await api.resume_box(query.from_user.id, box_id)
    if not resume_response.error:
        email_box = await api.get_user_box(query.from_user.id, box_id)
        if not email_box.error and email_box.data:
            await query.message.edit_text(
                get_boxes_mg.show_email_box_information(email_box.data),
                reply_markup=get_boxes_kb.email_box_details_keyboard(email_box.data)
            )
        elif email_box.error is EmailBoxNotFound:
            await query.message.edit_text(get_boxes_mg.email_box_not_found())
        elif email_box.error is APIInternalError:
            await query.message.answer(
                text=API_ERROR
            )
            await query.message.delete()
    elif resume_response.error is EmailBoxNotFound:
        await query.message.edit_text(get_boxes_mg.email_box_not_found())
    elif resume_response.error is APIInternalError:
        await query.message.answer(
            text=API_ERROR
        )
        await query.message.delete()


async def handle_back_to_email_boxes_list(query: types.CallbackQuery, state: FSMContext, api: APIClient) -> None:
    """Хендлер перехода в список почтовых ящиков."""
    email_boxes = await api.get_user_boxes(query.from_user.id)
    if not email_boxes.error and email_boxes.data:
        await query.message.edit_text(
            text=get_boxes_mg.choose_email_box(),
            reply_markup=get_boxes_kb.tracking_emails_keyboard(email_boxes.data)
        )
    elif email_boxes.error is UserBoxesNotFound:
        await query.message.answer(get_boxes_mg.no_tracking_emails())
        await query.message.delete()
    elif email_boxes.error is APIInternalError:
        await query.message.answer(
            text=API_ERROR,
        )
        await query.message.delete()


async def handle_delete_box(query: types.CallbackQuery, state: FSMContext, api: APIClient) -> None:
    """Хендлер удаления почтового ящика."""
    box_id = int(query.data.split(':')[1])
    delete_response = await api.delete_box(query.from_user.id, box_id)
    if not delete_response.error:
        await query.message.edit_text(
            text=get_boxes_mg.email_deleted(),
            reply_markup=get_boxes_kb.deletion_status_keyboard()
        )
    elif delete_response.error is EmailBoxNotFound:
        await query.message.edit_text(get_boxes_mg.email_box_not_found())
    elif delete_response.error is APIInternalError:
        await query.message.answer(
            text=API_ERROR,
        )
        await query.message.delete()


def register_my_boxes_handler(dp: Dispatcher) -> None:
    """Регистрация хендлеров для взаимодействия с почтовыми ящиками."""
    dp.register_message_handler(handle_get_boxes, Text('Мои почтовые ящики 🗃'), state='*')
    dp.register_callback_query_handler(
        handle_get_box,
        text_startswith='email_box:',
        state='*'
    )
    dp.register_callback_query_handler(
        handle_pause_box,
        text_startswith='pause_box:',
        state='*'
    )
    dp.register_callback_query_handler(
        handle_resume_box,
        text_startswith='resume_box:',
        state='*'
    )
    dp.register_callback_query_handler(
        handle_back_to_email_boxes_list,
        text='back_to_email_boxes_list',
        state='*'
    )
    dp.register_callback_query_handler(
        handle_delete_box,
        text_startswith='delete_box:',
        state='*'
    )
