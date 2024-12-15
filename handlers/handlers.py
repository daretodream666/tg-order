from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import API_TOKEN

bot = Bot(API_TOKEN)

import keyboards.keyboards as kb

from database import find_teachers, add_pupil, add_teacher, get_pupil_data, delete_forms_db

router = Router()


class Ask(StatesGroup):
    tg_id = State()
    name = State()
    year = State()
    faculty = State()
    subject = State()
    question = State()
    work_format = State()
    choose = State()
    waiting = State()


class Offer(StatesGroup):
    tg_id = State()
    name = State()
    year = State()
    faculty = State()
    subject = State()
    availability = State()
    work_format = State()
    answer = State()


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Привет! Я учебный помощник. Я помогу тебе найти поддержку в учебе или предложить свою помощь другим студентам.\nВыбери, что тебя интересует:', reply_markup=kb.main)

@router.message(Command("delete"))
async def delete_forms(message: Message, state: FSMContext):
    delete_forms_db(message.from_user.id)
    await state.clear()
    await message.answer("Вы удалили свои анкеты. Можете создать новую(-ые), написав команду /start.")

@router.callback_query(F.data == 'ask')
async def ask_one(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Ask.name)
    await callback.message.answer('Введите Ваше имя')

@router.message(Ask.name)
async def ask_two(message: Message, state: FSMContext):
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(name=message.text)
    await state.set_state(Ask.year)
    await message.answer('Выберите ваш курс', reply_markup=kb.year_kb)

@router.message(Ask.year)
async def ask_three(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(Ask.faculty)
    await message.answer('Выберите ваш факультет', reply_markup=kb.faculty_kb)

@router.message(Ask.faculty)
async def ask_four(message: Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    await state.set_state(Ask.subject)
    await message.answer('С какой дисциплиной вам нужна помощь?')

@router.message(Ask.subject)
async def ask_five(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(Ask.question)
    await message.answer('Опишите ваш запрос')

@router.message(Ask.question)
async def ask_six(message: Message, state: FSMContext):
    await state.update_data(question=message.text)
    await state.set_state(Ask.work_format)
    await message.answer('Какой формат работы вам удобнее?', reply_markup=kb.work_format_kb)

@router.message(Ask.work_format)
async def ask_final(message: Message, state: FSMContext):
    await state.update_data(work_format=message.text)
    data = await state.get_data()
    await state.set_state(Ask.choose)
    add_pupil(data)
    await message.answer('Отлично, твои данные сохранены! Давай найдем студента, который сможет тебе помочь. Просмотри карточки людей, готовых помочь, и отправь им запрос!')

    pupil_id = message.from_user.id
    teachers = find_teachers(pupil_id)
    if not teachers:
        await message.answer("К сожалению, мы не нашли подходящих помощников.")

    current_teacher_index = 0
    await state.update_data(teachers=teachers, current_teacher_id=list(teachers.keys())[current_teacher_index], current_teacher_index=0)
    
    await send_teacher_card(message, state)

async def send_teacher_card(message: Message, state: FSMContext):
    data = await state.get_data()
    teachers = data['teachers']
    current_teacher_id = data.get('current_teacher_id', 0)

    teacher = teachers[current_teacher_id]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать", callback_data=f"choose_{current_teacher_id}")],
        [InlineKeyboardButton(text="Показать ещё", callback_data="next_teacher")]
    ])
    
    await message.answer(
        f"Имя: {teacher['name']}\n"
        f"Курс: {teacher['year']}\n"
        f"Факультет: {teacher['faculty']}\n"
        f"Удобное время для занятий: {teacher['availability']}\n"
        f"Удобный формат занятий: {teacher['work_format']}",
        reply_markup=keyboard
    )

@router.callback_query(F.data == "next_teacher", StateFilter(Ask.choose))
async def show_next_teacher(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    teachers = data['teachers']
    current_teacher_index = data.get('current_teacher_index', 0)

    new_index = current_teacher_index + 1
    if new_index < len(teachers): 
        await state.update_data(current_teacher_index=new_index)
        await send_teacher_card(callback.message, state)  
    else:
        await callback.message.answer("Это все учителя.")
    await callback.answer()

@router.callback_query(F.data.startswith("choose_"), StateFilter(Ask.choose))
async def select_teacher(callback: CallbackQuery, state: FSMContext):
    teacher_id = int(callback.data.split('_')[1]) 
    data = await state.get_data()
    teachers = data['teachers']
    
    teacher = teachers[teacher_id]
    
    await state.set_state(Ask.waiting)
    await callback.message.answer(f"Отлично! Я отправил твою заявку. Как только {teacher['name']} примет ее, я дам тебе знать!")

    response_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Принять", callback_data=f"accept_{callback.from_user.id}"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{callback.from_user.id}")
        ]
    ])
    
    pupil_data = get_pupil_data(callback.from_user.id)
    teacher_message = (
        f"Вас просят о помощи!\n"
        f"Имя: {pupil_data[0]}\n"
        f"Курс: {pupil_data[1]}\n"
        f"Факультет: {pupil_data[2]}\n"
        f"Дисциплина: {pupil_data[3]}\n"
        f"С чем нужна помощь?: {pupil_data[4]}"
    )
    await bot.send_message(chat_id=teacher_id, text=teacher_message, reply_markup=response_kb)
    await callback.answer()

@router.callback_query(F.data == 'offer')
async def ask_one(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Offer.name)
    await callback.message.answer('Введите Ваше имя')

@router.message(Offer.name)
async def ask_two(message: Message, state: FSMContext):
    await state.update_data(tg_id=message.from_user.id)
    await state.update_data(name=message.text)
    await state.set_state(Offer.year)
    await message.answer('Выберите ваш курс', reply_markup=kb.year_kb)

@router.message(Offer.year)
async def ask_three(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(Offer.faculty)
    await message.answer('Выберите ваш факультет', reply_markup=kb.faculty_kb)

@router.message(Offer.faculty)
async def ask_four(message: Message, state: FSMContext):
    await state.update_data(faculty=message.text)
    await state.set_state(Offer.subject)
    await message.answer('С какой дисциплиной вы можете помочь?')

@router.message(Offer.subject)
async def ask_five(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(Offer.availability)
    await message.answer('Когда Вам удобно заниматься?')

@router.message(Offer.availability)
async def ask_six(message: Message, state: FSMContext):
    await state.update_data(availability=message.text)
    await state.set_state(Offer.work_format)
    await message.answer('Какой формат работы вам удобнее?', reply_markup=kb.work_format_kb)

@router.message(Offer.work_format)
async def ask_final(message: Message, state: FSMContext):
    await state.update_data(work_format=message.text)
    data = await state.get_data()
    add_teacher(data)
    await message.answer('Ваш профиль сохранен! Теперь я буду уведомлять вас о заявках от студентов, которым требуется помощь.')
    await state.clear()

@router.callback_query(F.data.startswith('accept_'))
async def accept_student(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data.split('_')[1])

    await bot.send_message(chat_id=student_id, text=f"Учитель @{callback.from_user.username} принял вашу заявку!")
    await callback.message.edit_text("Вы приняли заявку от ученика.", reply_markup=None)

@router.callback_query(F.data.startswith('reject_'))
async def reject_student(callback: CallbackQuery, state: FSMContext):
    student_id = int(callback.data.split('_')[1])

    await bot.send_message(chat_id=student_id, text=f"Учитель отклонил вашу заявку.")
    await callback.message.edit_text("Вы отклонили заявку от ученика.", reply_markup=None)

