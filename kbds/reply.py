# Импорты связанные с aiogram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Код файла 

del_kbd = ReplyKeyboardRemove()

startkbd = ReplyKeyboardBuilder()

startkbd.add(
    KeyboardButton(text="🎥 Конвертировать в кружочек"),
    KeyboardButton(text="📄 Конвертировать в GIF"),
    KeyboardButton(text="🎞 Конвертировать в webm"),
    KeyboardButton(text='🎞 Конвертировать gif в webm'),
    KeyboardButton(text='🖼 Конвертировать изображение в webm'),
    KeyboardButton(text='🖼 Сжать изображение'),
    KeyboardButton(text='Отмена действия')
)

startkbd.adjust(1,1,2,1,1)