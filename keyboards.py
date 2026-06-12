from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Главное меню для Студента
def get_student_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📊 Моя статистика"))
    return builder.as_markup(resize_keyboard=True)

# Главное меню для Админа
def get_admin_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="👥 Все студенты"))
    builder.row(KeyboardButton(text="⚙️ Админ-панель"))
    return builder.as_markup(resize_keyboard=True)

# Инлайн кнопки действий в Админ-панели
def get_admin_actions_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✏️ Изменить посещаемость", callback_data="admin_attendance"))
    builder.row(InlineKeyboardButton(text="💯 Изменить баллы", callback_data="admin_points"))
    return builder.as_markup()

# Список студентов (инлайн)
def get_students_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Иванов Иван", callback_data="student_1001"))
    builder.row(InlineKeyboardButton(text="Петрова Анна", callback_data="student_1002"))
    return builder.as_markup()

# Список предметов (инлайн)
def get_courses_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Математика", callback_data="course_Математика"))
    builder.row(InlineKeyboardButton(text="Физика", callback_data="course_Физика"))
    builder.row(InlineKeyboardButton(text="Программирование", callback_data="course_Программирование"))
    return builder.as_markup()