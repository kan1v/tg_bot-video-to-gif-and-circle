# Импорты связанные с aiogram 
import shutil
from PyPDF2 import PdfReader
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Bot
from aiogram.types import FSInputFile

# Импорты связанные с moviepy
from moviepy import VideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Crop import Crop

# Импорты связанные с ffmpeg
import subprocess
import imageio_ffmpeg as ffmpeg

# Импорты для работы с докс и пдф файлами 
from docx import Document
import pypandoc

# Импорты связанные с PIL для работы с кружочками 
from PIL import Image, ImageDraw

# Импорты связанные с numpy 
import numpy as np

# Импорт logging для отслеживания логов
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
    "Я **VideoMasterBot** 🎬 — твой помощник для обработки видео!\n"
    "С помощью меня ты можешь:\n"
    "1️⃣ Конвертировать видео в WebM для стикеров.\n"
    "2️⃣ Создавать видеокружочки (для аватарок и других целей).\n"
    "3️⃣ Превращать видео в GIF-анимацию.\n"
    "4️⃣ Преобразовывать GIF в формат WebM.\n\n"
    "Просто выбери нужную функцию или отправь мне файл, и я всё сделаю за тебя! 😊\n\n"
    "Если не знаешь с чего начать, выбери команду из меню ниже."
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

#Определение состояния для обработки видео-кружочков
class VideoToCircleMessage(StatesGroup):
    video = State()

# Хендлер для команды или нажатия кнопки
@user_private_router.message(or_f(Command('/circle'), F.text.lower() == "🎥 конвертировать в кружочек"))
async def get_video_for_circle(message: types.Message, state: FSMContext):
    await state.set_state(VideoToCircleMessage.video)
    await message.answer('Пожалуйста, отправьте видео для конвертации в кружочек.')
    logging.info("Запрос на отправку видео для конвертации в кружочек.")

@user_private_router.message(VideoToCircleMessage.video)
async def process_video_circle_to_message(message: types.Message, bot: Bot, state: FSMContext):
    video_message = message.video
    if not video_message:
        await message.answer("Пожалуйста, отправьте видео.")
        return

    # Проверка доступности FFmpeg
    if not shutil.which("ffmpeg"):
        await message.answer("Ошибка: FFmpeg не установлен или не найден в PATH.")
        return

    # Пути для временного хранения файлов
    file_info = await bot.get_file(video_message.file_id)
    video_path = os.path.join("temp", f"{video_message.file_id}.mp4")
    output_path = os.path.join("temp", f"{video_message.file_id}_circle.mp4")
    os.makedirs("temp", exist_ok=True)

    # Скачиваем видео
    await bot.download_file(file_info.file_path, video_path)

    try:
        await message.answer("⏳ Обрабатываю видео для кружочка...")

        # Команда для FFmpeg
        command = [
    "ffmpeg",
    "-i", video_path,  # Входное видео
    "-vf", "crop='min(iw,ih)':'min(iw,ih)',scale=320:320,format=yuva420p",  # Исправление фильтра
    "-vcodec", "libx264",
    "-acodec", "aac",
    "-preset", "ultrafast",
    "-y", output_path  # Выходной файл
]


        # Выполнение команды FFmpeg
        subprocess.run(command, check=True, stderr=subprocess.PIPE, text=True)

        # Отправка обработанного видео как video_message
        await message.answer_video_note(
            video_note=FSInputFile(output_path),
            caption="Ваше видео-кружочек готово! 🔵"
        )

    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg error: {e.stderr}")
        await message.answer(f"Произошла ошибка при обработке видео: {e.stderr}")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer(f"Произошла ошибка: {e}")
    finally:
        # Очистка временных файлов
        if os.path.exists("temp"):
            shutil.rmtree("temp")

    # Сброс состояния
    await state.clear()

# Определение состояния для обработки видео
class VideoToStickerMessage(StatesGroup):
    video = State()

# Хендлер для команды или нажатия кнопки
@user_private_router.message(or_f(Command('/sticker'), F.text.lower() == "🎞 конвертировать в webm"))
async def get_video_for_sticker(message: types.Message, state: FSMContext):
    await state.set_state(VideoToStickerMessage.video)
    await message.answer('Пожалуйста, отправьте видео для конвертации в стикер (формат WebM).')
    logging.info("Запрос на отправку видео для конвертации в стикер.")

# Хендлер для обработки отправленного видео
@user_private_router.message(VideoToStickerMessage.video)
async def process_video_to_sticker(message: types.Message, bot: Bot, state: FSMContext):
    video_message = message.video
    if not video_message:
        await message.answer("Пожалуйста, отправьте видео.")
        return

    # Пути для временного хранения файлов
    file_info = await bot.get_file(video_message.file_id)
    video_path = os.path.join("temp", f"{video_message.file_id}.mp4")
    output_path = os.path.join("temp", f"{video_message.file_id}_sticker.webm")
    os.makedirs("temp", exist_ok=True)

    # Скачиваем видео
    await bot.download_file(file_info.file_path, video_path)

    try:
        await message.answer("⏳ Обрабатываю видео для стикера...")

        # Команда для сжатия и преобразования видео в WebM
        command = [
    "ffmpeg",
    "-i", video_path,  # Входной файл
    "-vf", "crop='min(iw,ih)':'min(iw,ih)',scale=512:512,format=yuva420p",  # Обрезка, масштабирование, альфа-канал
    "-c:v", "libvpx-vp9",  # Кодек VP9
    "-b:v", "100k",  # Ограничение битрейта
    "-pix_fmt", "yuva420p",  # Формат пикселей
    "-r", "30",  # Ограничение FPS
    "-an",  # Удаление аудиопотока
    "-y",  # Перезапись выходного файла
    output_path  # Путь к выходному файлу
]

        # Выполнение команды FFmpeg
        subprocess.run(command, check=True)

        # Открытие файла через InputFile
        document = FSInputFile(output_path)

        # Отправка документа
        await message.answer_document(
    document=document,
    caption="Ваш видео стикер готов! 🎉"
)


    except subprocess.CalledProcessError as e:
        await message.answer(f"Произошла ошибка при обработке видео: {e}")
        logging.error(f"Ошибка FFmpeg: {e}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        logging.error(f"Ошибка: {e}")
    finally:
        # Удаление временных файлов
        for path in [video_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

    # Сброс состояния
    await state.clear()

# Определение состояния для обработки GIF
class GifToWebMMessage(StatesGroup):
    gif = State()

# Хендлер для команды или нажатия кнопки
@user_private_router.message(or_f(Command('/gifwebm'), F.text.lower() == "🎞 конвертировать gif в webm"))
async def get_gif_for_webm(message: types.Message, state: FSMContext):
    await state.set_state(GifToWebMMessage.gif)
    await message.answer('Пожалуйста, отправьте GIF для конвертации в WebM.')
    logging.info("Запрос на отправку GIF для конвертации в WebM.")

# Хендлер для обработки отправленного GIF
@user_private_router.message(GifToWebMMessage.gif)
async def process_gif_to_webm(message: types.Message, bot: Bot, state: FSMContext):
    gif_message = message.document or message.animation
    if not gif_message:
        await message.answer("Пожалуйста, отправьте GIF-файл.")
        return

    # Пути для временного хранения файлов
    file_info = await bot.get_file(gif_message.file_id)
    gif_path = os.path.join("temp", f"{gif_message.file_id}.gif")
    output_path = os.path.join("temp", f"{gif_message.file_id}.webm")
    os.makedirs("temp", exist_ok=True)

    # Скачиваем GIF
    await bot.download_file(file_info.file_path, gif_path)

    try:
        await message.answer("⏳ Обрабатываю GIF для конвертации в WebM...")

        # Проверка информации о GIF файле с помощью ffprobe
        ffprobe_command = [
            "ffprobe", "-v", "error", "-show_format", "-show_streams", gif_path
        ]
        ffprobe_output = subprocess.run(ffprobe_command, capture_output=True, text=True)
        if ffprobe_output.returncode != 0:
            await message.answer(f"Ошибка при проверке GIF: {ffprobe_output.stderr}")
            logging.error(f"Ошибка FFprobe: {ffprobe_output.stderr}")
            return

        # Команда FFmpeg для преобразования GIF в WebM с ограничениями по времени, размеру и разрешению
        command = [
    "ffmpeg",
    "-t", "3",  # Обрезка до 3 секунд
    "-i", gif_path,  # Входной GIF
    "-vf", "scale='if(gte(iw,ih),512,-1)':'if(gte(iw,ih),-1,512)'",  # Масштабирование до 512x512, сохраняя пропорции
    "-c:v", "libvpx-vp9",  # Кодек VP9 для WebM
    "-b:v", "256k",  # Ограничение битрейта до 256 KB
    "-pix_fmt", "yuv420p",  # Формат пикселей
    "-r", "30",  # Ограничение FPS
    "-y",  # Перезапись выходного файла
    output_path  # Путь к выходному WebM
]


        # Выполнение команды FFmpeg и логирование ошибок
        ffmpeg_output = subprocess.run(command, capture_output=True, text=True)
        if ffmpeg_output.returncode != 0:
            await message.answer(f"Ошибка при конвертации GIF в WebM: {ffmpeg_output.stderr}")
            logging.error(f"Ошибка FFmpeg: {ffmpeg_output.stderr}")
            return

        # Проверка размера файла и при необходимости сжатие
        file_size = os.path.getsize(output_path)
        if file_size > 256 * 1024:  # Если размер больше 256KB, сжимаем
            command = [
                "ffmpeg",
                "-i", output_path,  # Входной WebM
                "-c:v", "libvpx-vp9",  # Кодек VP9
                "-b:v", "256k",  # Ограничение битрейта
                "-y",  # Перезапись выходного файла
                output_path  # Путь к выходному WebM
            ]
            subprocess.run(command, check=True)

        # Открытие файла через InputFile
        document = FSInputFile(output_path)

        # Отправка WebM файла пользователю
        await message.answer_document(
            document=document,
            caption="Ваш WebM файл готов! 🎉"
        )

    except subprocess.CalledProcessError as e:
        await message.answer(f"Произошла ошибка при обработке GIF: {e}")
        logging.error(f"Ошибка FFmpeg: {e}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        logging.error(f"Ошибка: {e}")
    finally:
        # Удаление временных файлов
        for path in [gif_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

    # Сброс состояния
    await state.clear()

# Определение состояния для обработки изображения
class ImageToWebMMessage(StatesGroup):
    image = State()

# Хендлер для команды или нажатия кнопки
@user_private_router.message(or_f(Command('/imagetowebm'), F.text.lower() == "🖼 конвертировать изображение в webm"))
async def get_image_for_webm(message: types.Message, state: FSMContext):
    await state.set_state(ImageToWebMMessage.image)
    await message.answer('Пожалуйста, отправьте изображение для конвертации в WebM.')
    logging.info("Запрос на отправку изображения для конвертации в WebM.")

# Хендлер для обработки отправленного изображения
@user_private_router.message(ImageToWebMMessage.image)
async def process_image_to_webm(message: types.Message, bot: Bot, state: FSMContext):
    image_message = message.document or message.photo[-1]
    if not image_message:
        await message.answer("Пожалуйста, отправьте изображение в формате PNG или JPEG.")
        return

    # Пути для временного хранения файлов
    file_info = await bot.get_file(image_message.file_id)
    image_path = os.path.join("temp", f"{image_message.file_id}.png")
    output_path = os.path.join("temp", f"{image_message.file_id}.webm")
    os.makedirs("temp", exist_ok=True)

    # Скачиваем изображение
    await bot.download_file(file_info.file_path, image_path)

    try:
        await message.answer("⏳ Обрабатываю изображение для конвертации в WebM...")

        # Команда FFmpeg для преобразования изображения в WebM
        command = [
            "ffmpeg",
            "-loop", "1",  # Цикличный показ изображения
            "-i", image_path,  # Входное изображение
            "-vf", "scale=100:100",  # Масштабирование до 100x100
            "-c:v", "libvpx-vp9",  # Кодек VP9 для WebM
            "-b:v", "256k",  # Битрейт
            "-pix_fmt", "yuva420p",  # Поддержка альфа-канала (прозрачный фон)
            "-t", "3",  # Длительность видео 3 секунды
            "-y",  # Перезапись выходного файла
            output_path  # Путь к выходному WebM
        ]

        # Выполнение команды FFmpeg и логирование ошибок
        ffmpeg_output = subprocess.run(command, capture_output=True, text=True)
        if ffmpeg_output.returncode != 0:
            await message.answer(f"Ошибка при конвертации изображения в WebM: {ffmpeg_output.stderr}")
            logging.error(f"Ошибка FFmpeg: {ffmpeg_output.stderr}")
            return

        # Открытие файла через InputFile
        document = FSInputFile(output_path)

        # Отправка WebM файла пользователю
        await message.answer_document(
            document=document,
            caption="Ваш WebM файл с прозрачным фоном готов! 🎉"
        )

    except subprocess.CalledProcessError as e:
        await message.answer(f"Произошла ошибка при обработке изображения: {e}")
        logging.error(f"Ошибка FFmpeg: {e}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        logging.error(f"Ошибка: {e}")
    finally:
        # Удаление временных файлов
        for path in [image_path, output_path]:
            if os.path.exists(path):
                os.remove(path)

    # Сброс состояния
    await state.clear()


# Состояния
class ResizeImageMessage(StatesGroup):
    image = State()
    height = State()
    width = State()

# Хендлер для команды или нажатия кнопки
@user_private_router.message(or_f(Command('/resizeimage'), F.text.lower() == "🖼 сжать изображение"))
async def get_image_for_resizing(message: types.Message, state: FSMContext):
    await state.set_state(ResizeImageMessage.image)
    await message.answer('Пожалуйста, отправьте изображение для изменения размера.')
    logging.info("Запрос на отправку изображения для изменения размера.")

# Хендлер для получения изображения
@user_private_router.message(ResizeImageMessage.image)
async def ask_height(message: types.Message, bot: Bot, state: FSMContext):
    image_message = message.document or message.photo[-1]
    if not image_message:
        await message.answer("Пожалуйста, отправьте изображение в формате PNG или JPEG.")
        return

    # Сохраняем файл во временное хранилище
    file_info = await bot.get_file(image_message.file_id)
    input_path = os.path.join("temp", f"{image_message.file_id}.jpg")
    os.makedirs("temp", exist_ok=True)
    await bot.download_file(file_info.file_path, input_path)

    # Сохраняем путь к изображению в FSM
    await state.update_data(input_path=input_path)

    # Переходим к запросу высоты
    await state.set_state(ResizeImageMessage.height)
    await message.answer("Введите желаемую высоту изображения (в пикселях):")

# Хендлер для получения высоты
@user_private_router.message(ResizeImageMessage.height)
async def ask_width(message: types.Message, state: FSMContext):
    try:
        height = int(message.text)
        if height <= 0:
            raise ValueError("Высота должна быть положительным числом.")
        await state.update_data(height=height)
        await state.set_state(ResizeImageMessage.width)
        await message.answer("Введите желаемую ширину изображения (в пикселях):")
    except ValueError:
        await message.answer("Введите корректное положительное число для высоты.")

# Хендлер для получения ширины
@user_private_router.message(ResizeImageMessage.width)
async def resize_image(message: types.Message, state: FSMContext):
    try:
        width = int(message.text)
        if width <= 0:
            raise ValueError("Ширина должна быть положительным числом.")

        # Данные из FSM
        data = await state.get_data()
        input_path = data["input_path"]
        height = data["height"]
        output_path = os.path.join("temp", f"{os.path.basename(input_path).split('.')[0]}_resized.png")

        # Открываем и изменяем изображение
        with Image.open(input_path) as img:
            img = img.convert("RGBA")  # Учитываем прозрачность
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            img.save(output_path, format="PNG")

        # Отправка обработанного изображения пользователю
        resized_image = FSInputFile(output_path)
        await message.answer_document(
            document=resized_image,
            caption=f"Ваше изображение успешно изменено на {width}x{height}! 🎉"
        )
    except ValueError:
        await message.answer("Введите корректное положительное число для ширины.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке изображения: {e}")
        logging.error(f"Ошибка: {e}")
    finally:
        # Удаление временных файлов
        for path in [data.get("input_path"), output_path]:
            if path and os.path.exists(path):
                os.remove(path)

    # Сброс состояния
    await state.clear()



