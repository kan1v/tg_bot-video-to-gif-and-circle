# Импорты связанные с aiogram 
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
from aiogram.types import FSInputFile

# Импорты связанные с moviepy
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from PIL import Image, ImageDraw
import numpy as np
import logging

# Импорты стандартных библиотек python
import os

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



# Определение состояния для второго функционала 
class VideoToGif(StatesGroup):
    video = State()

# Настроим логирование
logging.basicConfig(level=logging.INFO)

@user_private_router.message(or_f(Command('/gif'), F.text.lower() == "📄 конвертировать в gif"))
async def get_video_for_circle(message: types.Message, state: FSMContext):
    await state.set_state(VideoToGif.video)
    await message.answer('Пожалуйста отправьте видео для конвертации в кружочек')
    logging.info("Запрос на отправку видео для конвертации в кружочек.")


@user_private_router.message(VideoToGif.video)
async def process_video_circle(message: types.Message, bot, state: FSMContext):
    video_message = message.video
    if not video_message:
        await message.answer('Пожалуйста отправьте видео.')
        return

    # Получение пути к видео
    file_info = await bot.get_file(video_message.file_id)
    video_path = os.path.join("temp", f"{video_message.file_id}.mp4")
    output_path = os.path.join("temp", f"{video_message.file_id}_circle.mp4")
    os.makedirs("temp", exist_ok=True)

    await bot.download_file(file_info.file_path, video_path)

    try:
        await message.answer("⏳ Обрабатываю видео...")

        # Загружаем видео
        clip = VideoFileClip(video_path)
        fps = clip.fps
        w, h = clip.size
        center = (w // 2, h // 2)
        radius = min(w, h) // 2

        # Создаем круглую маску
        def create_circle_mask(size, center, radius):
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse(
                (
                    center[0] - radius, center[1] - radius,
                    center[0] + radius, center[1] + radius
                ),
                fill=255
            )
            return np.array(mask)

        mask = create_circle_mask((w, h), center, radius)

        # Папка для временных кадров
        frames_dir = os.path.join("temp", "frames")
        os.makedirs(frames_dir, exist_ok=True)

        # Конвертация видео в кадры
        frames = []
        for i, frame in enumerate(clip.iter_frames(dtype="uint8")):
            frame_image = Image.fromarray(frame)
            frame_image.putalpha(Image.fromarray(mask))
            frame_path = os.path.join(frames_dir, f"frame_{i:04d}.png")
            frame_image.save(frame_path)
            frames.append(frame_path)

        # Создание нового видео из обработанных кадров
        from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

        new_clip = ImageSequenceClip(frames, fps=fps)
        new_clip.write_videofile(output_path, codec="libx264", fps=fps)

        # Отправка обработанного видео пользователю
        await message.answer_document(types.FSInputFile(output_path), caption="Ваше GIF видео готово! 🎥")

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке видео: {e}")
    finally:
        # Очистка временных файлов
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        if os.path.exists(frames_dir):
            for frame_file in os.listdir(frames_dir):
                os.remove(os.path.join(frames_dir, frame_file))
            os.rmdir(frames_dir)

    # Сброс состояния
    await state.clear()

# Определение состояния для функционала конвертации видео в кружочек
class VideoToCircle(StatesGroup):
    video = State()

@user_private_router.message(or_f(Command('/circle'), F.text.lower() == "🎥 конвертировать в кружочек"))
async def get_video_for_circle(message: types.Message, state: FSMContext):
    await state.set_state(VideoToCircle.video)
    await message.answer('Пожалуйста, отправьте видео для конвертации в кружочек.')
    logging.info("Запрос на отправку видео для конвертации в кружочек.")

@user_private_router.message(VideoToCircle.video)
async def process_video_circle(message: types.Message, bot: Bot, state: FSMContext):
    video_message = message.video
    if not video_message:
        await message.answer('Пожалуйста, отправьте видео.')
        return

    # Создаем временные пути
    file_info = await bot.get_file(video_message.file_id)
    video_path = os.path.join("temp", f"{video_message.file_id}.mp4")
    output_path = os.path.join("temp", f"{video_message.file_id}_circle.mp4")
    os.makedirs("temp", exist_ok=True)

    await bot.download_file(file_info.file_path, video_path)

    try:
        await message.answer("⏳ Обрабатываю видео...")

        # Загружаем видео
        clip = VideoFileClip(video_path)
        fps = clip.fps
        w, h = clip.size
        center = (w // 2, h // 2)
        radius = min(w, h) // 2

        # Создаем круглую маску
        def create_circle_mask(size, center, radius):
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse(
                (
                    center[0] - radius, center[1] - radius,
                    center[0] + radius, center[1] + radius
                ),
                fill=255
            )
            return np.array(mask)

        mask = create_circle_mask((w, h), center, radius)

        # Применяем маску к каждому кадру
        def apply_circle_mask(frame):
            frame_image = Image.fromarray(frame)
            frame_image = frame_image.convert("RGBA")
            mask_image = Image.fromarray(mask).convert("L")
            frame_image.putalpha(mask_image)
            return np.array(frame_image)

        # Применяем маску ко всем кадрам видео
        new_clip = clip.fl_image(apply_circle_mask)
        new_clip.write_videofile(output_path, codec="libx264", fps=fps, audio=True)

        # Отправка обработанного видео пользователю
        if not os.path.exists(output_path):
            await message.answer("Ошибка: обработанный файл не был создан.")
            return

        video_file = FSInputFile(output_path)
        await message.answer_video(video_file, caption="Ваше видео в кружочке готово! 🎥")

    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке видео: {e}")
        logging.error(f"Ошибка при обработке видео: {e}", exc_info=True)
    finally:
        # Очистка временных файлов
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_path):
            os.remove(output_path)

    # Сброс состояния
    await state.clear()
    logging.info("Состояние сброшено.")
