import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Импортируем настройки и клавиатуры из твоих файлов лабы
from config import BOT_TOKEN, ADMIN_ID
from keyboards import (
    get_student_keyboard,
    get_admin_keyboard,
    get_students_inline_keyboard,
    get_courses_inline_keyboard,
    get_admin_actions_keyboard,
)

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализируем бота и диспетчер напрямую (Hiddify в режиме TUN сам всё проксирует)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Состояния для машины состояний (FSM)
class AdminState(StatesGroup):
    waiting_for_student = State()
    waiting_for_course = State()
    waiting_for_value = State()

# Временная база данных студентов в виде словаря
students_db = {
    1001: {
        "name": "Иванов Иван",
        "courses": {
            "Математика": {"attendance": 90, "points": 72},
            "Физика": {"attendance": 85, "points": 88},
            "Программирование": {"attendance": 95, "points": 95},
        }
    },
    1002: {
        "name": "Петрова Анна",
        "courses": {
            "Математика": {"attendance": 78, "points": 65},
            "Физика": {"attendance": 82, "points": 70},
            "Программирование": {"attendance": 88, "points": 80},
        }
    }
}

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    # ПРОВЕРКА: Если ID пользователя совпадает с ID админа из config.py
    if message.from_user.id == int(ADMIN_ID):
        kb = get_admin_keyboard() # Выдаем админские кнопки
    else:
        kb = get_student_keyboard() # Всем остальным выдаем кнопки студента
        
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        "Я бот для просмотра дисциплин, посещаемости и баллов.\n"
        "Используй кнопки ниже для навигации.",
        reply_markup=kb
    )

# Лочит кнопку «Все студенты» даже со смайликами
@dp.message(F.text.contains("Все студенты"))
async def show_all_students(message: types.Message):
    if not students_db:
        await message.answer("Список студентов пуст.")
        return
        
    text = "Список студентов:\n\n"
    for sid, student in students_db.items():
        text += f"Студент: {student['name']}\n"
        for course, data in student["courses"].items():
            text += f"  {course}: посещ. {data['attendance']}%, баллы {data['points']}\n"
        text += "\n"
    await message.answer(text.strip())

# Лочит кнопку «Админ-панель» в любом формате
@dp.message(F.text.contains("Админ-панель"))
async def admin_panel(message: types.Message):
    # Дополнительная проверка безопасности, чтобы обычный пользователь не зашел по тексту
    if message.from_user.id != int(ADMIN_ID):
        await message.answer("У вас нет прав администратора.")
        return
    await message.answer("Выберите действие для редактирования:", reply_markup=get_admin_actions_keyboard())

# Нажатие на инлайн-кнопку "Изменить посещаемость"
@dp.callback_query(F.data == "admin_attendance")
async def admin_change_attendance(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите студента для изменения посещаемости:", reply_markup=get_students_inline_keyboard())
    await state.set_state(AdminState.waiting_for_student)
    await state.update_data(action="attendance")

# Нажатие на инлайн-кнопку "Изменить баллы"
@dp.callback_query(F.data == "admin_points")
async def admin_change_points(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Выберите студента для изменения баллов:", reply_markup=get_students_inline_keyboard())
    await state.set_state(AdminState.waiting_for_student)
    await state.update_data(action="points")

# Ловим выбор студента в админке
@dp.callback_query(AdminState.waiting_for_student, F.data.startswith("student_"))
async def admin_student_chosen(callback: types.CallbackQuery, state: FSMContext):
    student_id = int(callback.data.split("_")[1])
    await state.update_data(student_id=student_id)
    await callback.message.edit_text("Выберите дисциплину:", reply_markup=get_courses_inline_keyboard())
    await state.set_state(AdminState.waiting_for_course)

# Ловим выбор предмета в админке
@dp.callback_query(AdminState.waiting_for_course, F.data.startswith("course_"))
async def admin_course_chosen(callback: types.CallbackQuery, state: FSMContext):
    course_name = callback.data.split("_")[1]
    await state.update_data(course_name=course_name)
    
    data = await state.get_data()
    action_name = "посещаемости" if data.get("action") == "attendance" else "баллов"
    
    await callback.message.edit_text(f"Введите новое числовое значение для {action_name}:")
    await state.set_state(AdminState.waiting_for_value)

# Ловим число от пользователя и сохраняем изменения
@dp.message(AdminState.waiting_for_value)
async def save_value(message: types.Message, state: FSMContext):
    try:
        value = int(message.text)
    except ValueError:
        await message.answer("Ошибка! Введите целое числовое значение.")
        return

    data = await state.get_data()
    student_id = data.get("student_id")
    course_name = data.get("course_name")
    action = data.get("action")

    if student_id not in students_db or course_name not in students_db[student_id]["courses"]:
        await message.answer("Ошибка: студент или дисциплина не найдены в базе.")
        await state.clear()
        return

    field = "attendance" if action == "attendance" else "points"
    students_db[student_id]["courses"][course_name][field] = value
    
    field_name = "посещаемость" if action == "attendance" else "баллы"
    
    await message.answer(
        f"Данные успешно обновлены! ✅\n\n"
        f"Студент: {students_db[student_id]['name']}\n"
        f"Дисциплина: {course_name}\n"
        f"Новая {field_name}: {value}"
    )
    await state.clear()
    await message.answer("Выберите следующее действие:", reply_markup=get_admin_actions_keyboard())

# Лочит кнопку «Моя статистика»
@dp.message(F.text.contains("Моя статистика"))
async def show_my_stats(message: types.Message):
    student = students_db[1001] 
    text = f"Ваша статистика ({student['name']}):\n\n"
    for course, data in student["courses"].items():
        text += f"  {course}: посещ. {data['attendance']}%, баллы {data['points']}\n"
    await message.answer(text)

# Функция запуска процесса polling
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())