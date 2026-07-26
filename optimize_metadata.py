import json
import os
import time
import pandas as pd
import requests


def call_local_ollama(prompt):
    """Вызов локальной нейросети Ollama (100% без лимитов и ключей)"""
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False,
        "format": "json",  # Требуем строго JSON формат
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            res_json = response.json()
            return json.loads(res_json["response"])
        else:
            print(f"   Ошибка Ollama: status {response.status_code}")
            return None
    except Exception as e:
        print(f"   Ошибка связи с Ollama: {e}")
        return None


def main():
    if not os.path.exists("backup.json"):
        print(" ОШИБКА: backup.json не найден. Запустите auth_and_backup.py")
        return

    with open("backup.json", "r", encoding="utf-8") as f:
        videos = json.load(f)

    print(
        f"🚀 Локальная SEO & CTR оптимизация {len(videos)} видео через Ollama..."
    )

    optimized_data = []

    for index, video in enumerate(videos, 1):
        print(f"[{index}/{len(videos)}] Оптимизация: {video['title'][:40]}...")

        prompt = f"""
        You are a top-tier YouTube Growth Strategist specializing in ethnic music, instrumental covers, Native American flute, and folk instruments.
        Target Audience: UK and Worldwide English listeners.
        
        Original Metadata:
        - Title: {video['title']}
        - Description: {video['description']}
        - Tags: {video['tags']}
        
        TASKS:
        1. TITLE: Create a catchy, high-CTR English title (under 70 chars). Combine instrument/song name with vibe/use-case (e.g. Meditation, Healing, Deep Focus).
        2. DESCRIPTION: Write a 100-150 word SEO description in English. First sentence must be a strong hook. Add 3-5 hashtags at the end.
        3. TAGS: Provide 12-15 relevant, high-search English tags separated by commas.
        
        Return ONLY a JSON object with keys: "new_title", "new_description", "new_tags".
        """

        seo_res = call_local_ollama(prompt)

        if seo_res:
            optimized_data.append(
                {
                    "video_id": video["video_id"],
                    "old_title": video["title"],
                    "new_title": seo_res.get("new_title", ""),
                    "old_description": video["description"],
                    "new_description": seo_res.get("new_description", ""),
                    "old_tags": video["tags"],
                    "new_tags": seo_res.get("new_tags", ""),
                    "views": video["views"],
                    "status": "APPROVED",
                }
            )
            print(f"   🔥 Новый заголовок: {seo_res.get('new_title', '')}")
        else:
            print("   Пропущено.")

    if optimized_data:
        df = pd.DataFrame(optimized_data)
        df.to_excel("approved.xlsx", index=False)
        print(
            f"\n УСПЕХ! Все {len(optimized_data)} видео обработаны локально и сохранены в approved.xlsx!"
        )


if __name__ == "__main__":
    main()