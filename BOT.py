import logging
import sys
import os
from dotenv import load_dotenv
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import asyncio

class Form(StatesGroup):
    waiting_for_pair_name = State()
    waiting_for_number = State()
    waiting_for_weekday = State()
    waiting_for_week_type = State()
    waiting_for_description = State()
    waiting_for_link = State()  # Новий стан для посилання

# Загружаем токен бота
load_dotenv()
TOKEN = os.getenv("TOKEN")




# Клавіатура з кнопками "Скасувати" та "Головне меню"
def get_cancel_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏹ Скасувати"), KeyboardButton(text="🏠 Головне меню")]
        ],
        resize_keyboard=True
    )

# Словник для назв днів тижня
WEEKDAYS = {
    "mon": "Понеділок",
    "tue": "Вівторок",
    "wed": "Середа",
    "thu": "Четвер",
    "fri": "П'ятниця",
    "sat": "Субота",
    "sun": "Неділя"
}


# Инициализируем диспетчер
dp = Dispatcher()

# Главное меню
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сьогодні")],
            [KeyboardButton(text="Мій розклад")],
            [KeyboardButton(text="Управління групами")]
        ],
        resize_keyboard=True
    )

# Обработчик команды /start
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Оберіть опцію:", reply_markup=main_menu())

# Обработчик кнопки "Сьогодні"
@dp.message(F.text == "Сьогодні")
async def today_schedule(message: Message):
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1.ОПІ", callback_data="ОПІ")],
            [InlineKeyboardButton(text="2.Фізика", callback_data="Фізика")]
        ]
    )
    await message.answer("Виберіть пару", reply_markup=inline_keyboard)

# Обработчик кнопки "Мій розклад"
@dp.message(F.text == "Мій розклад")
async def my_schedule(message: Message):
    # Inline-клавиатура (ОПІ и Фізика)
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1.ОПІ", callback_data="ОПІ")],
            [InlineKeyboardButton(text="2.Фізика", callback_data="Фізика")]
        ]
    )

    # Reply-клавиатура (Створити, Переглянути розклад, Головне)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Створити")],
            [KeyboardButton(text="Переглянути розклад")],
            [KeyboardButton(text="Головне меню")]
        ],
        resize_keyboard=True
    )
    await message.answer("Додаткові опції:", reply_markup=keyboard)



@dp.message(F.text == "Переглянути розклад")
async def view_schedule(message: Message):
    # 1. Inline-клавиатура с выбором пары
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1.ОПІ : 9:00", callback_data="ОПІ")],
            [InlineKeyboardButton(text="2.Фізика: 10:20", callback_data="Фізика")]
        ]
    )
    await message.answer("Оберіть пару:", reply_markup=inline_keyboard)

    # 2. Reply-клавиатура (появится внизу экрана)
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Парний тиждень")],
            [KeyboardButton(text="Непарний тиждень")],
            [KeyboardButton(text="Головне меню")]
        ],
        resize_keyboard=True
    )
    # Пустое сообщение, чтобы не выводить лишний текст
    await message.answer("Додаткові опції", reply_markup=keyboard)



@dp.message(F.text == "Створити")
async def create_pair(message: types.Message, state: FSMContext):
    await message.answer("Введіть назву онлайн пари:", reply_markup=get_cancel_menu())
    await state.set_state(Form.waiting_for_pair_name)


# Обробник для кнопки "Скасувати"
@dp.message(F.text == "⏹ Скасувати")
async def cancel_creation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Створення пари скасовано", reply_markup=get_cancel_menu())


# Обробник для кнопки "Головне меню"
@dp.message(F.text == "🏠 Головне меню")
async def main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ви повернулись у головне меню", reply_markup=get_cancel_menu())


@dp.message(Form.waiting_for_pair_name)
async def process_pair_name(message: types.Message, state: FSMContext):
    await state.update_data(pair_name=message.text)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(1, 4)],
            [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(4, 7)],
            [InlineKeyboardButton(text=str(i), callback_data=str(i)) for i in range(7, 10)],
        ]
    )
    await message.answer("Оберіть номер пари:", reply_markup=keyboard)
    await message.answer("Або використайте кнопки нижче:", reply_markup=get_cancel_menu())
    await state.set_state(Form.waiting_for_number)


@dp.callback_query(Form.waiting_for_number)
async def process_number(callback: types.CallbackQuery, state: FSMContext):
    if callback.data not in [str(i) for i in range(1, 10)]:
        await callback.answer("Будь ласка, оберіть номер від 1 до 9")
        return

    await state.update_data(pair_number=callback.data)

    weekday_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Пн", callback_data="mon"),
                InlineKeyboardButton(text="Вт", callback_data="tue"),
                InlineKeyboardButton(text="Ср", callback_data="wed"),
            ],
            [
                InlineKeyboardButton(text="Чт", callback_data="thu"),
                InlineKeyboardButton(text="Пт", callback_data="fri"),
                InlineKeyboardButton(text="Сб", callback_data="sat"),
            ],
            [
                InlineKeyboardButton(text="Нд", callback_data="sun"),
            ]
        ]
    )

    await callback.message.edit_text(
        text=f"Обрано пару №{callback.data}. Оберіть день тижня:",
        reply_markup=weekday_kb
    )
    await callback.message.answer("Або використайте кнопки нижче:", reply_markup=get_cancel_menu())
    await state.set_state(Form.waiting_for_weekday)
    await callback.answer()


@dp.callback_query(Form.waiting_for_weekday)
async def process_weekday(callback: types.CallbackQuery, state: FSMContext):
    if callback.data not in WEEKDAYS:
        await callback.answer("Будь ласка, оберіть день тижня зі списку")
        return

    await state.update_data(weekday=callback.data)

    week_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Парний", callback_data="even"),
                InlineKeyboardButton(text="Непарний", callback_data="odd"),
                InlineKeyboardButton(text="Всі тижні", callback_data="all")
            ]
        ]
    )

    await callback.message.edit_text(
        text=f"Обраний день: {WEEKDAYS[callback.data]}. Оберіть тип тижня:",
        reply_markup=week_kb
    )
    await callback.message.answer("Або використайте кнопки нижче:", reply_markup=get_cancel_menu())
    await state.set_state(Form.waiting_for_week_type)
    await callback.answer()


@dp.callback_query(Form.waiting_for_week_type)
async def process_week_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.data not in ["even", "odd", "all"]:
        await callback.answer("Будь ласка, оберіть тип тижня з пропонованих")
        return

    await state.update_data(week_type=callback.data)

    skip_button = InlineKeyboardButton(text="Пропустити", callback_data="skip_description")
    add_button = InlineKeyboardButton(text="Додати опис", callback_data="add_description")

    desc_kb = InlineKeyboardMarkup(inline_keyboard=[[skip_button, add_button]])

    await callback.message.edit_text(
        text="Бажаєте додати опис до пари?",
        reply_markup=desc_kb
    )
    await callback.message.answer("Або використайте кнопки нижче:", reply_markup=get_cancel_menu())
    await state.set_state(Form.waiting_for_description)
    await callback.answer()


@dp.callback_query(Form.waiting_for_description, F.data == "skip_description")
async def skip_description(callback: types.CallbackQuery, state: FSMContext):
    # Пропускаємо опис і переходимо до посилання
    link_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустити", callback_data="skip_link"),
             InlineKeyboardButton(text="Додати посилання", callback_data="add_link")]
        ]
    )
    await callback.message.edit_text(
        text="Бажаєте додати посилання до пари?",
        reply_markup=link_kb
    )
    await state.set_state(Form.waiting_for_link)
    await callback.answer()


@dp.callback_query(Form.waiting_for_description, F.data == "add_description")
async def ask_for_description(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Будь ласка, введіть опис для цієї пари:",
        reply_markup=None
    )
    await callback.message.answer("Або використайте кнопки нижче:", reply_markup=get_cancel_menu())
    await callback.answer()


@dp.message(Form.waiting_for_description)
async def process_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)

    link_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустити", callback_data="skip_link"),
             InlineKeyboardButton(text="Додати посилання", callback_data="add_link")]
        ]
    )
    await message.answer("Бажаєте додати посилання до пари?", reply_markup=link_kb)
    await state.set_state(Form.waiting_for_link)


@dp.callback_query(Form.waiting_for_link, F.data == "skip_link")
async def skip_link(callback: types.CallbackQuery, state: FSMContext):
    await finish_pair_creation(callback, state, link=None)


@dp.callback_query(Form.waiting_for_link, F.data == "add_link")
async def ask_for_link(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Будь ласка, введіть посилання для цієї пари (наприклад, https://meet.google.com/abc-def-ghi):",
        reply_markup=None
    )
    await callback.message.answer("Або використайте кнопки нижче:", reply_markup=get_cancel_menu())
    await callback.answer()


@dp.message(Form.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    await finish_pair_creation(message, state, link=message.text)


async def finish_pair_creation(source: types.Message | types.CallbackQuery, state: FSMContext, link: str | None):
    data = await state.get_data()

    week_types = {
        "even": "Парний тиждень",
        "odd": "Непарний тиждень",
        "all": "Всі тижні"
    }

    pair_data = {
        "name": data["pair_name"],
        "number": data["pair_number"],
        "weekday": WEEKDAYS[data["weekday"]],
        "week_type": week_types[data["week_type"]],
        "description": data.get("description"),
        "link": link
    }

    # Тут можна зберегти pair_data у базу даних
    print("Створена пара:", pair_data)

    response_text = (
        f"✅ Пара успішно створена!\n\n"
        f"📌 Назва: {pair_data['name']}\n"
        f"🔢 Номер: {pair_data['number']}\n"
        f"📅 День: {pair_data['weekday']}\n"
        f"🔄 Тип тижня: {pair_data['week_type']}\n"
    )

    if pair_data['description']:
        response_text += f"📝 Опис: {pair_data['description']}\n"
    else:
        response_text += "📝 Опис: не додано\n"

    if pair_data['link']:
        response_text += f"🔗 Посилання: {pair_data['link']}"
    else:
        response_text += "🔗 Посилання: не додано"

    if isinstance(source, types.Message):
        await source.answer(response_text, reply_markup=get_cancel_menu())
    else:
        await source.message.edit_text(response_text)
        await source.message.answer("Готово!", reply_markup=get_cancel_menu())

    await state.clear()
    if isinstance(source, types.CallbackQuery):
        await source.answer()





# Обработчик кнопки "Головне"
@dp.message(F.text == "Головне меню")
async def back_to_main_menu(message: Message):
    await message.answer("Ви повернулись в головне меню:", reply_markup=main_menu())

# Обработчик callback-кнопок (ссылки)
@dp.callback_query()
async def callback_handler(callback: CallbackQuery):
    if callback.data == "ОПІ":
        await callback.message.answer("https://meet.google.com/yhy-vjvx-dup?authuser=0")
    elif callback.data == "Фізика":
        await callback.message.answer("https://us05web.zoom.us/j/82766032885?pwd=Js0VEfywvF7931Cr7hrRys8Gr0EAaT.1")
    await callback.answer()


# Функция запуска бота
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())


    # await callback.message.edit_text(
    #     f"Создана пара:\n"
    #     f"Название: {pair_name}\n"
    #     f"Номер: {selected_number}"
    #