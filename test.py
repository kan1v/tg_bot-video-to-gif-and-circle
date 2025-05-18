from yt_dlp import YoutubeDL

def download_tiktok_video(url):
    ydl_opts = {
        'outtmpl': 'video.mp4',  # Имя файла для сохранения
        'format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

download_tiktok_video("https://www.tiktok.com/@koreanasha/video/7483106116981755152?is_from_webapp=1&sender_device=pc")