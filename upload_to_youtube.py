import os
import time
import pandas as pd
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_youtube_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def main():
    if not os.path.exists("approved.xlsx"):
        print("ОШИБКА: Файл approved.xlsx не найден!")
        return

    df = pd.read_excel("approved.xlsx")
    youtube = get_youtube_service()

    print(f"🚀 Дожимаем оставшиеся 18 видео с гарантированным исправлением...\n")

    updated_count = 0

    for index, row in df.iterrows():
        video_id = str(row["video_id"]).strip()
        new_title = str(row["new_title"]).strip() if pd.notna(row["new_title"]) else ""
        new_desc = str(row["new_description"]).strip() if pd.notna(row["new_description"]) else ""
        
        # Обрезаем заголовок до безопасной длины (максимум 90 символов)
        if len(new_title) > 90:
            new_title = new_title[:87] + "..."

        # Обработка тегов
        if pd.notna(row["new_tags"]):
            raw_tags = [t.strip() for t in str(row["new_tags"]).split(",") if t.strip()]
            # Берем первые 8 тегов, чтобы точно не вылезти за лимиты
            new_tags = raw_tags[:8]
        else:
            new_tags = ["Native American Flute", "Meditation Music", "Handcrafted Instruments"]

        if not new_title:
            continue

        try:
            # Получаем текущий snippet
            res = youtube.videos().list(part="snippet", id=video_id).execute()
            if not res["items"]:
                continue

            snippet = res["items"][0]["snippet"]

            # Пропускаем уже обновленные ролик
            if snippet["title"] == new_title:
                continue

            print(f"[{index+1}/{len(df)}] Исправление {video_id}: '{new_title[:40]}...'")

            # ВАЖНО: Принудительно задаем категорию Music ("10") и дефолтный язык
            snippet["title"] = new_title
            snippet["description"] = new_desc
            snippet["tags"] = new_tags
            snippet["categoryId"] = "10"  # 10 = Music в YouTube API
            snippet["defaultLanguage"] = "en"
            snippet["defaultAudioLanguage"] = "en"

            youtube.videos().update(
                part="snippet",
                body={
                    "id": video_id,
                    "snippet": snippet
                }
            ).execute()

            updated_count += 1
            print("   ✅ Успешно обновлено!")

        except Exception as e:
            # Если теги всё ещё вызывают сомнения у YouTube, пробуем обновить без тегов
            try:
                snippet["tags"] = []
                youtube.videos().update(
                    part="snippet",
                    body={"id": video_id, "snippet": snippet}
                ).execute()
                updated_count += 1
                print("   ✅ Успешно обновлено (без тегов)!")
            except Exception as inner_e:
                print(f"   ❌ Ошибка: {inner_e}")

        time.sleep(0.5)

    print(f"\n🎉 Все готово! Успешно обновлено роликов: {updated_count}.")

if __name__ == "__main__":
    main()