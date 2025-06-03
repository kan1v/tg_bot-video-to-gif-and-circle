# Импорты связанные с aiogram 
from aiogram.types import BotCommand

private = [
    BotCommand(command='/start', description='Старт общения с ботом'),
    BotCommand(command='/gif', description='Преобразование видео в GIF'),
    BotCommand(command='/circle', description='Видео преобразованое в кружочек'),
    BotCommand(command='/sticker', description='Создание webm файла'),
    BotCommand(command='/gifwebm', description='Создание из gif - webm файл'),
    BotCommand(command='/imagetowebm', description='Создание из картинки - webm файл для стикеров'),
    BotCommand(command='/resizeimage', description='Изменение разрешения для картинки'),
    BotCommand(command='downloadvideotiktok', description='Скачивание видео из тт без водяного знака'),
    BotCommand(command='circle2video', description='Сделать из кружочка обычное видео')
    
    
]