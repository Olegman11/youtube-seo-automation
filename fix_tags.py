import pandas as pd

# Словарь релевантных тегов под разные инструменты
TAG_PRESETS = {
    "cajon": "WiseWood, Cajon, Portable Cajon, Travel Cajon, Cajon Drum, Percussion, Handcrafted Cajon, Sound Demo, Acoustic Percussion, Cajon Solo, Rhythm",
    "talharpa": "WiseWood, Talharpa, Tagelharpa, Viking Music, Jouhikko, Bowed Lyre, Pagan Music, Handcrafted Instrument, Sound Demo, Medieval Instrument",
    "flute": "WiseWood, Native American Flute, Pimak, Native Flute, Meditation Music, Handcrafted Flute, Sound Demo, Relaxing Flute, Woodwind Instrument, Flute Solo",
    "ocarina": "WiseWood, Ocarina, Handcrafted Ocarina, Ceramic Flute, Ocarina Sound Demo, Acoustic Music, Folk Instrument",
    "default": "WiseWood, Handcrafted Instrument, Sound Demo, Acoustic Music, Relaxation, Focus Music, Handmade"
}

def generate_tags_for_row(row):
    title = str(row.get("new_title", "")).lower()
    desc = str(row.get("new_description", "")).lower()
    text = title + " " + desc

    tags = []
    
    # Базовый брендовый тег
    tags.append("WiseWood")
    tags.append("WiseWood Music")

    # Детекция инструмента
    if "cajon" in text or "кахон" in text:
        tags.extend(["Cajon", "Portable Cajon", "Travel Cajon", "Cajon Drum", "Percussion", "Handcrafted Cajon", "Sound Demo", "Rhythm", "Percussion Showcase"])
    elif "talharpa" in text or "viking" in text or "tagelharpa" in text:
        tags.extend(["Talharpa", "Tagelharpa", "Viking Music", "Bowed Lyre", "Jouhikko", "Pagan Music", "Medieval Instrument", "Sound Demo"])
    elif "ocarina" in text or "окарина" in text:
        tags.extend(["Ocarina", "Ceramic Ocarina", "Ocarina Music", "Handcrafted Ocarina", "Sound Demo"])
    elif "quena" in text:
        tags.extend(["Quena", "Quena Flute", "Andean Flute", "Woodwind", "Sound Demo"])
    elif "pimak" in text or "flute" in text or "флейта" in text or "love flute" in text:
        tags.extend(["Native American Flute", "Native Flute", "Pimak", "Meditation Flute", "Handcrafted Flute", "Relaxing Flute", "Woodwind", "Sound Demo", "Healing Music"])
    else:
        tags.extend(["Handcrafted Instrument", "Sound Demo", "Acoustic Showcase", "Relaxation", "Focus Music"])

    # Доп. общие теги для раскрутки
    tags.extend(["Handmade Instrument", "Acoustic Test", "Instrument Showcase"])

    # Убираем дубликаты, сохраняя порядок
    unique_tags = []
    for t in tags:
        if t not in unique_tags:
            unique_tags.append(t)

    return ", ".join(unique_tags)

def main():
    if not pd.io.common.file_exists("approved.xlsx"):
        print("ОШИБКА: Файл approved.xlsx не найден!")
        return

    df = pd.read_excel("approved.xlsx")

    print("🏷️ Проверка и заполнение тегов для всех видео...\n")

    updated_count = 0
    for index, row in df.iterrows():
        current_tags = str(row.get("new_tags", "")).strip()

        # Если тегов нет, написано 'nan', или их слишком мало
        if not current_tags or current_tags.lower() == "nan" or len(current_tags) < 15:
            new_tags = generate_tags_for_row(row)
            df.at[index, "new_tags"] = new_tags
            updated_count += 1
            print(f"[{index+1}/{len(df)}] ➕ Заполнены теги для {row['video_id']}: {new_tags[:60]}...")
        else:
            print(f"[{index+1}/{len(df)}] ✅ Теги уже есть: {current_tags[:50]}...")

    df.to_excel("approved.xlsx", index=False)
    print(f"\n🎉 Готово! Заполнено/обновлено тегов у {updated_count} видео из {len(df)}.")

if __name__ == "__main__":
    main()