# Импорты связанные с aiogram 
from aiogram.types import BotCommand

private = [
    BotCommand(command='/start', description='Старт общения с ботом'),
    BotCommand(command='/gif', description='Преобразование видео в GIF'),
    BotCommand(command='/videotocircle', description='Видео преобразованое в кружочек')
]