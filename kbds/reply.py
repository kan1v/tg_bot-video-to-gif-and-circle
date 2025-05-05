# Импорты связанные с aiogram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Код файла 

del_kbd = ReplyKeyboardRemove()

startkbd = ReplyKeyboardBuilder()

startkbd.add(
    KeyboardButton(text="🎥 Конвертировать в кружочек"),
    KeyboardButton(text="📄 Конвертировать в GIF")
)

startkbd.adjust(1,1)