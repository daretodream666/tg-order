from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Я хочу помочь', callback_data='offer')],
    [InlineKeyboardButton(text='Мне нужна помощь', callback_data='ask')]
])

year_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='1'), KeyboardButton(text='2')],
    [KeyboardButton(text='3'), KeyboardButton(text='4')],
    [KeyboardButton(text='5'), KeyboardButton(text='6')]
], resize_keyboard=True,one_time_keyboard=True,input_field_placeholder='Выберите ваш курс')

faculty_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='ИУ'), KeyboardButton(text='ИБМ'), KeyboardButton(text='МТ'), KeyboardButton(text='СМ')],
    [KeyboardButton(text='БМТ'), KeyboardButton(text='РЛ'), KeyboardButton(text='Э')],
    [KeyboardButton(text='РК'), KeyboardButton(text='ФН'), KeyboardButton(text='Л')],
    [KeyboardButton(text='ЮР'), KeyboardButton(text='СГН'), KeyboardButton(text='МТКП')]
], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите ваш факультет')

work_format_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Очный')],
    [KeyboardButton(text='Заочный')],
    [KeyboardButton(text='Не имеет значения')]
], resize_keyboard=True, one_time_keyboard=True, input_field_placeholder='Выберите формат работы')

teacher_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Выбрать')],
    [KeyboardButton(text='Показать ещё')]
], resize_keyboard=True, one_time_keyboard=True)