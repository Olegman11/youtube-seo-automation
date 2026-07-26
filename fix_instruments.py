import pandas as pd
import json
import requests
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import googleapiclient.discovery

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_youtube_service():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def generate_correct_metadata(original_title, current_title):
    """Строгая генерация названий с помощью Ollama без 'галлюцинаций'"""
    
    prompt = f"""
    You are an expert YouTube SEO specialist for hand-crafted musical instruments by "WiseWood".
    
    Original Title: "{original_title}"
    Current Generated Title: "{current_title}"
    
    INSTRUCTIONS:
    1. Identify the EXACT instrument from the original title (e.g., Portable Cajon, Travel Cajon, Mini Cajon, Talharpa, Pimak Flute, Ocarina).
    2. NEVER confuse Cajon with Flute or Talharpa!
    3. If it is a Cajon, the title MUST contain "WiseWood Cajon" or "Portable Cajon" or "Travel Cajon Drum Showcase / Sound Demo".
    4. Focus on Sound Demo, Handcrafted Instrument Showcase, Travel Percussion, Acoustic Demo, or Sound Test.
    
    Return ONLY a JSON object:
    {{
        "instrument": "Cajon / Flute / Talharpa / etc.",
        "new_title": "Clean, Catchy, Accurately Spelled YouTube Title (max 85 chars)",
        "new_description": "Accurate description highlighting the WiseWood handcrafted instrument sound demo, features, and specs. Add relevant hashtags like #Cajon #WiseWood #Percussion #SoundDemo."
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
        print(f"Ошибка обращения к Ollama: {e}")
    return None

def main():
    if not pd.io.common.file_exists("approved.xlsx"):
        print("ОШИБКА: Файл approved.xlsx не найден!")
        return

    df = pd.read_excel("approved.xlsx")
    youtube = get_youtube_service()

    print("🔍 Анализ и исправление названий/описаний на основе реальных инструментов...\n")

    updated_rows = []

    for index, row in df.iterrows():
        video_id = str(row["video_id"]).strip()
        current_title = str(row["new_title"])
        # Если есть колонка со старым заголовком — берем ее, иначе используем текущий
        original_title = str(row.get("original_title", current_title))

        print(f"[{index+1}/{len(df)}] Проверка {video_id}...")
        
        fixed_data = generate_correct_metadata(original_title, current_title)

        if fixed_data:
            new_title = fixed_data.get("new_title", current_title)
            new_desc = fixed_data.get("new_description", row["new_description"])
            instrument = fixed_data.get("instrument", "Unknown")

            print(f"   🎯 Определен инструмент: {instrument}")
            print(f"   ✏️ Новый заголовок: {new_title}")

            # Обновляем структуру данных
            df.at[index, "new_title"] = new_title
            df.at[index, "new_description"] = new_desc

            # Загружаем сразу на YouTube
            try:
                res = youtube.videos().list(part="snippet", id=video_id).execute()
                if res["items"]:
                    snippet = res["items"][0]["snippet"]
                    snippet["title"] = new_title[:90]
                    snippet["description"] = new_desc
                    snippet["categoryId"] = "10" # Music

                    youtube.videos().update(
                        part="snippet",
                        body={"id": video_id, "snippet": snippet}
                    ).execute()
                    print("   ✅ Успешно обновлено на YouTube!")

            except Exception as e:
                print(f"   ❌ Ошибка загрузки на YouTube: {e}")

        time.sleep(0.5)

    # Сохраняем исправленный эксель
    df.to_excel("approved.xlsx", index=False)
    print("\n🎉 Все названия и описания успешно исправлены и синхронизированы!")

if __name__ == "__main__":
    main()