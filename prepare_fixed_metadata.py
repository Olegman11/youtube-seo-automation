import pandas as pd
import json
import requests
import time

def generate_correct_metadata(original_title, current_title):
    prompt = f"""
    You are an expert YouTube SEO specialist for hand-crafted musical instruments by "WiseWood".
    
    Original Title: "{original_title}"
    Current Title: "{current_title}"
    
    INSTRUCTIONS:
    1. Identify the EXACT instrument from the original title or current title (e.g., Portable Cajon, Travel Cajon, Mini Cajon, Talharpa, Pimak Flute, Ocarina, Bamboo Flute).
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
        print(f"Ошибка Ollama: {e}")
    return None

def main():
    if not pd.io.common.file_exists("approved.xlsx"):
        print("ОШИБКА: Файл approved.xlsx не найден!")
        return

    df = pd.read_excel("approved.xlsx")

    print("🔍 Исправление названий локально через Ollama (без запросов к YouTube)...\n")

    for index, row in df.iterrows():
        video_id = str(row["video_id"]).strip()
        current_title = str(row.get("new_title", ""))
        original_title = str(row.get("original_title", current_title))

        print(f"[{index+1}/{len(df)}] Обработка {video_id}...")
        
        fixed_data = generate_correct_metadata(original_title, current_title)

        if fixed_data:
            new_title = fixed_data.get("new_title", current_title)
            new_desc = fixed_data.get("new_description", row.get("new_description", ""))
            instrument = fixed_data.get("instrument", "Unknown")

            print(f"   🎯 Инструмент: {instrument}")
            print(f"   ✏️ Заголовок: {new_title}")

            df.at[index, "new_title"] = new_title
            df.at[index, "new_description"] = new_desc

        time.sleep(0.2)

    df.to_excel("approved.xlsx", index=False)
    print("\n🎉 Готово! Все исправленные заголовки и описания сохранены в approved.xlsx!")

if __name__ == "__main__":
    main()