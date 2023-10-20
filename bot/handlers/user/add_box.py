from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config.config import API_ERROR, CRYPTO_KEY
from crypto.encryption_service import CryptoService
from keyboards.inline import add_email as add_email_kb
from keyboards.reply import user_reply
from messages.user import add_email as add_email_mg
from states.email_states import EmailBoxState
from utils.api_client import APIClient
from utils.exceptions import (
    APIInternalError,
    AvailableServicesNotFound,
    EmailCredsInvalid,
)
from utils.validators import validate_email


async def handle_add_email(message: types.Message, state: FSMContext, api: APIClient) -> None:
    """Хендлер сообщения о добавлении почтового ящика."""
    await state.reset_state()
    await state.reset_data()
    email_services = await api.get_services()
    if not email_services.error and email_services.data:
        await message.answer(
            text=add_email_mg.add_email_box_instruction(),
            reply_markup=user_reply.cancel_keyboard()
        )
        await message.answer(
            text=add_email_mg.choose_email_service(),
            reply_markup=add_email_kb.search_engines_keyboard(email_services.data),
        )
        await EmailBoxState.service.set()
    elif email_services.error is AvailableServicesNotFound:
        await message.answer(
            text=add_email_mg.no_available_services(),
            reply_markup=user_reply.bot_main_keyboard()
        )
    elif email_services.error is APIInternalError:
        await message.answer(
            text=API_ERROR,
            reply_markup=user_reply.bot_main_keyboard()
        )


async def handle_email_provider_choice(query: types.CallbackQuery, state: FSMContext) -> None:
    """Хендлер выбора почтового сервиса."""
    provider = query.data.split(':')[1]
    await state.update_data(service=provider)
    await query.message.edit_text(add_email_mg.add_email_box(), reply_markup=None)
    await EmailBoxState.email_address.set()


async def handle_email_input(message: types.Message, state: FSMContext) -> None:
    """Хендлер ввода email адреса."""
    email = message.text
    if not validate_email(email):
        await message.answer(add_email_mg.incorrect_email_address(), reply_markup=user_reply.cancel_keyboard())
        return
    await state.update_data(email_address=email)
    await message.answer(add_email_mg.add_email_password(), reply_markup=user_reply.cancel_keyboard())
    await EmailBoxState.password.set()


async def handle_password_input(message: types.Message, state: FSMContext) -> None:
    """Хендлер ввода пароля от почтового ящика."""
    crypto_service = CryptoService(CRYPTO_KEY)
    password = message.text
    encrypted_password = crypto_service.encrypt_password(password)
    await state.update_data(password=encrypted_password)
    await message.answer(add_email_mg.add_email_filter_value(), reply_markup=user_reply.cancel_keyboard())
    await message.delete()
    await EmailBoxState.filter_value.set()


async def handle_filters_value_input(message: types.Message, state: FSMContext) -> None:
    """Хендлер ввода значения фильтра."""
    box_filter = message.text
    if not validate_email(box_filter):
        await message.answer(add_email_mg.incorrect_email_address(), reply_markup=user_reply.cancel_keyboard())
        return
    current_data = await state.get_data()
    filters = current_data.get('filters', [])
    filters.append({'filter_value': box_filter})
    await state.update_data(filters=filters)
    await message.answer(add_email_mg.add_email_filter_name(), reply_markup=user_reply.cancel_keyboard())
    await EmailBoxState.filter_name.set()


async def handle_filter_name_input(message: types.Message, state: FSMContext) -> None:
    """Хендлер ввода названия фильтра."""
    filter_name = message.text
    current_data = await state.get_data()
    current_data['filters'][-1]['filter_name'] = filter_name
    await state.update_data(filters=current_data['filters'])
    await message.answer(add_email_mg.filter_reminder_instruction(), reply_markup=user_reply.cancel_keyboard())
    await message.answer(add_email_mg.more_filters_question(), reply_markup=add_email_kb.more_filters_keyboard())


async def handle_add_more_filters_decision(query: types.CallbackQuery, state: FSMContext, api: APIClient) -> None:
    """Хендлер добавления дополнительных фильтров."""
    if query.data == 'add_more_filters':
        await query.message.edit_text(add_email_mg.add_next_email_filter_value())
        await EmailBoxState.filter_value.set()
    elif query.data == 'no_more_filters':
        data = await state.get_data()
        create_box_response = await api.create_box(query.from_user.id, data)
        if not create_box_response.error:
            await query.message.answer(
                add_email_mg.email_box_created(),
                reply_markup=user_reply.bot_main_keyboard()
            )
            await query.message.delete()
        elif create_box_response.error is EmailCredsInvalid:
            await query.message.answer(
                add_email_mg.incorrect_email_creds(),
                reply_markup=user_reply.bot_main_keyboard()
            )
            await query.message.delete()
        elif create_box_response.error is APIInternalError:
            await query.message.answer(
                text=API_ERROR,
                reply_markup=user_reply.bot_main_keyboard()
            )
            await query.message.delete()
        await state.reset_state()


def register_add_email_handler(dp: Dispatcher) -> None:
    """Регистрация хендлеров и колбеков для данного процесса."""
    dp.register_message_handler(handle_email_input, state=EmailBoxState.email_address)
    dp.register_message_handler(handle_password_input, state=EmailBoxState.password)
    dp.register_message_handler(handle_filters_value_input, state=EmailBoxState.filter_value)
    dp.register_message_handler(handle_filter_name_input, state=EmailBoxState.filter_name)
    dp.register_message_handler(handle_add_email, Text('Добавить почтовый ящик 📧'), state='*')
    dp.register_callback_query_handler(
        handle_email_provider_choice,
        text_startswith='service:',
        state=EmailBoxState.service
    )
    dp.register_callback_query_handler(
        handle_add_more_filters_decision,
        text=['add_more_filters', 'no_more_filters'],
        state=EmailBoxState.filter_name,
    )
