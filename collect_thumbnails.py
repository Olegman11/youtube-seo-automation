import os
import json
import shutil

# Укажите путь к папке output вашего ComfyUI
COMFY_OUTPUT_DIR = r"C:\ComfyUI_windows_portable\ComfyUI\output" 
TARGET_DIR = "thumbnails"

def main():
    if not os.path.exists("thumbnail_prompts.json"):
        print("❌ Файл thumbnail_prompts.json не найден!")
        return

    with open("thumbnail_prompts.json", "r", encoding="utf-8") as f:
        prompts = json.load(f)

    os.makedirs(TARGET_DIR, exist_ok=True)

    # Находим все сгенерированные файлы yt_thumb_*.png в порядке их создания
    files = [
        f for f in os.listdir(COMFY_OUTPUT_DIR) 
        if f.startswith("yt_thumb") and f.endswith(".png")
    ]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(COMFY_OUTPUT_DIR, x)))

    print(f"📦 Найдено {len(files)} файлов из ComfyUI. Связываем с ID видео...\n")

    for index, file_name in enumerate(files):
        if index >= len(prompts):
            break
        
        video_id = prompts[index]["video_id"]
        src = os.path.join(COMFY_OUTPUT_DIR, file_name)
        dst = os.path.join(TARGET_DIR, f"{video_id}.jpg")

        shutil.copy(src, dst)
        print(f"[{index+1}/{len(files)}] Скопировано: {file_name} -> {dst}")

    print("\n🎉 Все обложки собраны и переименованы в папку thumbnails/!")

if __name__ == "__main__":
    main()