import pandas as pd
import json
import requests
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Список нужных вам языков
TARGET_LANGUAGES = {
    "de": "German",
    "fr": "French",
    "uk": "Ukrainian",
    "ru": "Russian"
}

def get_youtube_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def translate_metadata(title, description, target_lang_code, target_lang_name):
    prompt = f"""
    You are a professional translator for YouTube metadata.
    Translate the following title and description into {target_lang_name}.
    Keep brand names like "WiseWood", "Cajon", "Pimak", "Talharpa" unchanged if appropriate.
    
    Title: "{title}"
    Description: "{description}"
    
    Return ONLY a JSON object:
    {{
        "title": "Translated Title (max 90 chars)",
        "description": "Translated Description"
    }}
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    try:
        res = requests.post(url, json=payload, timeout=60)
        if res.status_code == 200:
            return json.loads(res.json()["response"])
    except Exception as e:
        print(f"   ❌ Ошибка перевода на {target_lang_name}: {e}")
    return None

def main():
    if not pd.io.common.file_exists("approved.xlsx"):
        print("ОШИБКА: Файл approved.xlsx не найден!")
        return

    df = pd.read_excel("approved.xlsx")
    youtube = get_youtube_service()

    print("🌍 Запуск локализации на Немецкий, Французский, Украинский и Русский языки...\n")

    for index, row in df.iterrows():
        video_id = str(row["video_id"]).strip()
        title = str(row["new_title"])
        description = str(row["new_description"])

        print(f"[{index+1}/{len(df)}] Локализация видео {video_id}...")

        localizations = {}

        for lang_code, lang_name in TARGET_LANGUAGES.items():
            translated = translate_metadata(title, description, lang_code, lang_name)
            if translated:
                localizations[lang_code] = {
                    "title": translated.get("title", title)[:90],
                    "description": translated.get("description", description)
                }
                print(f"   ✅ Переведено на {lang_name}")

        if localizations:
            try:
                # Получаем текущие данные видео
                res = youtube.videos().list(part="snippet,localizations", id=video_id).execute()
                if res["items"]:
                    video = res["items"][0]
                    snippet = video["snippet"]
                    
                    # Устанавливаем базовый язык видео как английский
                    snippet["defaultLanguage"] = "en"
                    snippet["defaultAudioLanguage"] = "en"

                    # Загружаем локализации
                    youtube.videos().update(
                        part="snippet,localizations",
                        body={
                            "id": video_id,
                            "snippet": snippet,
                            "localizations": localizations
                        }
                    ).execute()
                    print("   🚀 Все 4 языка (DE, FR, UK, RU) успешно сохранены на YouTube!\n")

            except Exception as e:
                print(f"   ❌ Ошибка отправки на YouTube: {e}\n")

        time.sleep(0.5)

    print("🎉 Перевод и локализация всех роликов успешно завершены!")

if __name__ == "__main__":
    main()