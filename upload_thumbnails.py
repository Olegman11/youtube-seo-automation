import os
import time
import pandas as pd
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload

# Авторизация в YouTube API
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", SCOPES
    )
    credentials = flow.run_local_server(port=0)
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def upload_thumbnail(youtube, video_id, image_path):
    try:
        request = youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(image_path)
        )
        response = request.execute()
        return True
    except googleapiclient.errors.HttpError as e:
        print(f"❌ Ошибка загрузки для {video_id}: {e}")
        return False

def main():
    if not os.path.exists("thumbnails"):
        print("❌ Папка thumbnails не найдена!")
        return

    youtube = get_authenticated_service()
    
    # Получаем список готовых картинок
    image_files = [f for f in os.listdir("thumbnails") if f.endswith(".jpg") or f.endswith(".png")]
    print(f"🚀 Найдено {len(image_files)} обложек для загрузки на YouTube...\n")

    for index, filename in enumerate(image_files, 1):
        video_id = os.path.splitext(filename)[0]
        image_path = os.path.join("thumbnails", filename)

        print(f"[{index}/{len(image_files)}] Установка обложки для {video_id}...")
        
        success = upload_thumbnail(youtube, video_id, image_path)
        if success:
            print(f"   ✅ Обложка обновлена!")
        
        time.sleep(1) # Небольшая пауза между запросами

    print("\n🎉 Все доступные обложки успешно загружены на YouTube!")

if __name__ == "__main__":
    main()