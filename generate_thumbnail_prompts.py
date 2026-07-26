import json
import os
import random
import pandas as pd

# Варианты внешности для девушек с флейтами
FLUTE_APPEARANCES = [
    "stunning young Native American woman with long dark braided hair intertwined with white feathers",
    "breathtakingly beautiful Native American woman with long wavy obsidian hair and subtle tribal gold face marks",
    "gorgeous, highly attractive Native American girl with sleek straight black hair and a beaded leather headband",
    "strikingly beautiful Native American woman with elegant high-braided hair and turquoise-adorned braids",
    "alluring Native American beauty with loose wind-blown dark hair adorned with leather ribbons and small feathers"
]

# Варианты локаций для индейской флейты
FLUTE_LOCATIONS = [
    "on a high rocky canyon cliff during a dramatic golden hour sunset, soft light mist in the valley",
    "deep inside an enchanted pine forest near a calm crystal-clear mountain lake, gentle morning rays",
    "by a warm glowing bonfire near an authentic tribal lodge at twilight, starry night sky",
    "standing before a misty cascading waterfall surrounded by mossy rocks and lush greenery",
    "on top of a red rock mesa in Sedona during a breathtaking purple and orange dusk"
]

def get_flute_prompt(index):
    # Динамически меняем внешность и локацию
    appearance = FLUTE_APPEARANCES[index % len(FLUTE_APPEARANCES)]
    location = FLUTE_LOCATIONS[index % len(FLUTE_LOCATIONS)]

    return (
        f"Ultra realistic cinematic portrait of a {appearance}, "
        "flawless skin, alluring face, full sensuous lips, expressive captivating eyes. "
        "She is wearing a stylish low-cut leather top with intricate Native American beadwork, showcasing an attractive deep cleavage. "
        "ANATOMY: Perfectly realistic hands with exactly FIVE slender fingers on each hand, flawless hand structure. "
        "INSTRUMENT: She is gracefully holding and playing an authentic Native American Flute (Pimak). "
        "The flute is crafted from rich polished cedar wood with detailed hand-carved tribal totemic patterns, "
        "featuring a prominent wooden bird-shaped totem block at the top tied with genuine leather thongs, "
        "decorated with hanging eagle feathers, wooden beads, and clear hand-engraved text 'WiseWood' on the wooden barrel. "
        f"SETTING: {location}. "
        "Cinematic lighting, ultra detailed skin texture, 85mm lens photography, 8k resolution, masterpiece, 16:9 aspect ratio."
    )

def get_cajon_prompt():
    return (
        "Ultra realistic cinematic photography, gorgeous attractive boho girl with long wavy copper-red hair, "
        "flawless skin, captivating eyes. Wearing an alluring low-cut leather top showcasing an attractive cleavage. "
        "ANATOMY: Perfectly structured hands with precisely five fingers per hand. "
        "She is sitting on a handcrafted wooden Cajon drum, playfully tapping on it. "
        "The Cajon has clear hand-engraved text 'WiseWood' wood-burned into its wooden surface. "
        "Setting: Boho music festival field during golden hour, warm sunset bokeh background. 8k, masterpiece, 16:9 aspect ratio."
    )

def get_talharpa_prompt():
    return (
        "Cinematic portrait of a stunning attractive Nordic Viking woman with long platinum-white braided hair, "
        "piercing blue eyes. Wearing an alluring leather and fur corset top showcasing an attractive cleavage. "
        "ANATOMY: Flawless hands with exactly five fingers per hand. "
        "She holds an authentic wooden Viking Talharpa lyre with horsehair strings. "
        "The wooden body has clear hand-carved inscription reading 'WiseWood'. "
        "Setting: Dramatic misty Scandinavian fjords background, 8k resolution, masterpiece, 16:9 aspect ratio."
    )

def get_ocarina_prompt():
    return (
        "Ultra realistic photography of a gorgeous young woman with long dark wavy hair. "
        "Wearing an alluring woodland leather corset with a deep neckline. "
        "ANATOMY: Perfect hands with exactly five fingers on each hand. "
        "She holds a handcrafted wooden Ocarina with carved tribal patterns near her lips. "
        "The Ocarina has clean hand-engraved text 'WiseWood' visible on the wooden body. "
        "Setting: Enchanted sunlit forest with mossy rocks, 8k resolution, 16:9 aspect ratio."
    )

def detect_instrument(text):
    text_lower = str(text).lower()
    if any(k in text_lower for k in ["talharpa", "tagelharpa", "тальхарпа"]):
        return "talharpa"
    elif any(k in text_lower for k in ["cajon", "кахон"]):
        return "cajon"
    elif any(k in text_lower for k in ["ocarina", "окарина"]):
        return "ocarina"
    else:
        return "flute"

def main():
    if not os.path.exists("approved.xlsx"):
        print("❌ ОШИБКА: Файл approved.xlsx не найден!")
        return

    df = pd.read_excel("approved.xlsx")
    prompts_data = []

    print("🎨 Генерация уникальных разноплановых промптов с контролем анатомии рук (5 пальцев)...\n")

    flute_counter = 0

    for index, row in df.iterrows():
        video_id = str(row["video_id"]).strip()
        title = str(row.get("new_title", ""))
        tags = str(row.get("new_tags", ""))
        desc = str(row.get("new_description", ""))

        full_text = f"{title} {tags} {desc}"
        instrument = detect_instrument(full_text)

        if instrument == "flute":
            prompt = get_flute_prompt(flute_counter)
            flute_counter += 1
        elif instrument == "cajon":
            prompt = get_cajon_prompt()
        elif instrument == "talharpa":
            prompt = get_talharpa_prompt()
        else:
            prompt = get_ocarina_prompt()

        prompts_data.append({
            "video_id": video_id,
            "title": title,
            "instrument": instrument,
            "image_prompt": prompt,
            "filename": f"thumbnails/{video_id}.jpg"
        })

    os.makedirs("thumbnails", exist_ok=True)

    with open("thumbnail_prompts.json", "w", encoding="utf-8") as f:
        json.dump(prompts_data, f, ensure_ascii=False, indent=2)

    pd.DataFrame(prompts_data).to_excel("thumbnail_prompts.xlsx", index=False)

    print("🎉 Обновленные промпты с 5 пальцами и разной внешностью сохранены!")

if __name__ == "__main__":
    main()