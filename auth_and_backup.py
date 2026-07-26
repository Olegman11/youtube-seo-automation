import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery
import pandas as pd

# Разрешения для работы с YouTube API (чтение и запись)
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]


def get_authenticated_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("client_secret.json"):
                raise FileNotFoundError(
                    "Файл client_secret.json не найден! Положите его в папку проекта."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


def fetch_all_videos(youtube):
    print("Получаем ID плейлиста загрузок...")
    ch_request = youtube.channels().list(part="contentDetails", mine=True)
    ch_response = ch_request.execute()

    uploads_playlist_id = ch_response["items"][0]["contentDetails"][
        "relatedPlaylists"
    ]["uploads"]

    video_ids = []
    next_page_token = None

    print("Собираем список всех видео...")
    while True:
        playlist_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token,
        )
        playlist_response = playlist_request.execute()

        for item in playlist_response["items"]:
            video_ids.append(item["snippet"]["resourceId"]["videoId"])

        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break

    print(f"Найдено видео: {len(video_ids)}. Загружаем подробные метаданные...")

    videos_data = []
    # Обрабатываем видео блоками по 50 штук (лимит API)
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i : i + 50]
        videos_request = youtube.videos().list(
            part="snippet,statistics", id=",".join(batch_ids)
        )
        videos_response = videos_request.execute()

        for item in videos_response["items"]:
            snippet = item["snippet"]
            stats = item.get("statistics", {})

            video_info = {
                "video_id": item["id"],
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "tags": ", ".join(snippet.get("tags", [])),
                "category_id": snippet.get("categoryId", ""),
                "published_at": snippet.get("publishedAt", ""),
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0)),
                "thumbnail_url": snippet.get("thumbnails", {})
                .get("high", {})
                .get("url", ""),
            }
            videos_data.append(video_info)

    return videos_data


def main():
    youtube = get_authenticated_service()
    videos = fetch_all_videos(youtube)

    # 1. Сохраняем полный бэкап в JSON
    with open("backup.json", "w", encoding="utf-8") as f:
        json.dump(videos, f, ensure_ascii=False, indent=4)
    print("Успешно создан backup.json")

    # 2. Сохраняем таблицу для аудита в Excel
    df = pd.DataFrame(videos)
    df.to_excel("audit.xlsx", index=False)
    print("Успешно создан audit.xlsx")


if __name__ == "__main__":
    main()