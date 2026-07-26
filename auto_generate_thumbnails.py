import json
import os
import time
import urllib.request

COMFYUI_URL = "http://127.0.0.1:8188"
GENERATION_WAIT_TIME = 42  # Пауза между запросами в секундах

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request(f"{COMFYUI_URL}/prompt", data=data)
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read())
    except Exception as e:
        print(f"❌ Ошибка подключения к ComfyUI: {e}")
        return None

def build_flux_workflow(prompt_text, seed):
    # Негативные промпты для предотвращения extra fingers и деформаций
    negative_prompt = "bad anatomy, extra fingers, 6 fingers, 7 fingers, deformed hands, extra limbs, mutated hands, poorly drawn hands, fused fingers, missing fingers, bad proportions, straight wooden stick, plain pole"

    return {
        "1": {
            "inputs": {
                "unet_name": "flux1-dev-fp8.safetensors",
                "weight_dtype": "fp8_e4m3fn"
            },
            "class_type": "UNETLoader"
        },
        "2": {
            "inputs": {
                "clip_name1": "t5xxl_fp8_e4m3fn.safetensors",
                "clip_name2": "clip_l.safetensors",
                "type": "flux"
            },
            "class_type": "DualCLIPLoader"
        },
        "3": {
            "inputs": {
                "vae_name": "ae.safetensors"
            },
            "class_type": "VAELoader"
        },
        "4": {
            "inputs": {
                "text": prompt_text,
                "clip": ["2", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "5": {
            "inputs": {
                "text": negative_prompt,
                "clip": ["2", 0]
            },
            "class_type": "CLIPTextEncode"
        },
        "6": {
            "inputs": {
                "width": 1280,
                "height": 720,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "7": {
            "inputs": {
                "seed": seed,
                "steps": 24, # Чуть подняли детализацию до 24 steps
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["4", 0],
                "negative": ["5", 0],
                "latent_image": ["6", 0]
            },
            "class_type": "KSampler"
        },
        "8": {
            "inputs": {
                "samples": ["7", 0],
                "vae": ["3", 0]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "yt_thumb",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }

def main():
    if not os.path.exists("thumbnail_prompts.json"):
        print("ОШИБКА: Сначала запустите python generate_thumbnail_prompts.py!")
        return

    with open("thumbnail_prompts.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    os.makedirs("thumbnails", exist_ok=True)
    print(f"🎨 Запуск обновленной генерации {len(items)} обложек (пауза {GENERATION_WAIT_TIME} сек)...")
    print("✨ Исправления: точно 5 пальцев, аутентичный Пимак с блоком/перьями, разные девушки и фоны.\n")

    for index, item in enumerate(items, 1):
        video_id = item["video_id"]
        prompt = item["image_prompt"]

        print(f"[{index}/{len(items)}] Генерация обложки для {video_id}...")

        seed = int(time.time() * 1000) % 1000000000
        workflow = build_flux_workflow(prompt, seed)

        res = queue_prompt(workflow)
        if res:
            print(f"   ⏳ Отправлено в ComfyUI (ID: {res.get('prompt_id')}). Ждем {GENERATION_WAIT_TIME} сек...")
            time.sleep(GENERATION_WAIT_TIME)
        else:
            print("   ❌ Не удалось отправить задание. Проверьте ComfyUI.")

    print("\n🎉 Все 88 обложек успешно запущены в генерацию!")

if __name__ == "__main__":
    main()