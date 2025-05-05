# Импорты связанные с aiogram 
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

# Импорты связанные с файлами проекта 
from kbds.reply import del_kbd, startkbd

user_private_router = Router()

# Обработчик команды start 
@user_private_router.message(CommandStart())
async def start_cmd(message:types.Message):
    welcome_text = (
        "👋 Привет, {user_first_name}!\n\n"
        "Я бот для обработки видео! 📹\n"
        "С помощью меня ты можешь:\n"
        "1️⃣ Конвертировать видео в кружочек (для аватарок и других целей).\n"
        "2️⃣ Превратить видео в GIF-анимацию.\n\n"
        "Просто отправь мне видео, и я сделаю всё за тебя! 😊\n\n"
        "Выбери нужную функцию из меню ниже или отправь видео прямо сейчас."
    ).format(user_first_name=message.from_user.first_name)

    await message.answer(welcome_text, reply_markup=startkbd.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Выбирите действие:'
    ))


class VideoToGif(StatesGroup):
    video = State()

@user_private_router.message(or_f(Command('/videotogif'), F.text.lower() == '🎥 Конвертировать в кружочек'))
async def get_video(message: types.Message, state:FSMContext):
    await state.set_state(VideoToGif.video)
    await message.answer('Пожалуйста отправьте видео для конвертации в GIF', reply_markup=del_kbd)

@user_private_router.message(VideoToGif.video)
async def procces_video_gif(message:types.Message, state:FSMContext):
    video_message = message.answer_video
    if video_message:
        pass


