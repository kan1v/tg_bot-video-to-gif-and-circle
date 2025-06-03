# Импорты связанные с aiogram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# Код файла 

del_kbd = ReplyKeyboardRemove()

startkbd = ReplyKeyboardBuilder()

startkbd.add(
    KeyboardButton(text="🎥 Конвертировать в кружочек"),
    KeyboardButton(text='🎥 Кружочек в обычное видео'),
    KeyboardButton(text="📄 Конвертировать в GIF"),
    KeyboardButton(text="🎞 Конвертировать в webm"),
    KeyboardButton(text='🎞 Конвертировать gif в webm'),
    KeyboardButton(text='🖼 Конвертировать изображение в webm'),
    KeyboardButton(text='🖼 Сжать изображение'),
    KeyboardButton(text='🎥 Скачать Tik Tok видео'),
    KeyboardButton(text='❌ Отмена')
)

startkbd.adjust(2,1,2,1)

