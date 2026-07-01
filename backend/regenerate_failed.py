"""重新生成失败的 2 张三文鱼菜谱图片，并更新 mapping.json。"""
import os
import json
import hashlib
import urllib.parse
import urllib.request

IMG_API = "https://image.pollinations.ai/prompt"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "static", "recipes")

MISSING_RECIPES = [
    ("b89137cc-189b-46e4-b0cd-e0b45eebbb07", "香煎三文鱼",
     "A plate of pan-seared salmon fillet, golden crispy skin side up, pink-orange salmon flesh, with a lemon wedge, on a white plate, overhead view, food photography, appetizing"),
    ("b0ab49f2-ae58-4e81-9c0c-15e4e1b19129", "三文鱼头豆腐汤",
     "A bowl of Chinese salmon head tofu soup, milky white broth with fish head pieces and white tofu cubes, sprinkled with scallions, in a ceramic bowl, overhead view, food photography"),
]


def slugify(name: str) -> str:
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:12]


def generate_image(prompt: str, output_path: str, seed: int, retries: int = 3) -> bool:
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{IMG_API}/{encoded_prompt}?width=512&height=512&nologo=true&seed={seed}&model=flux"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                if resp.status == 200 and "image" in resp.headers.get("Content-Type", ""):
                    data = resp.read()
                    if len(data) > 2000:
                        with open(output_path, "wb") as f:
                            f.write(data)
                        return True
                    print(f"  [WARN] Image too small: {len(data)} bytes (attempt {attempt+1})")
                else:
                    print(f"  [WARN] status={resp.status}, type={resp.headers.get('Content-Type')} (attempt {attempt+1})")
        except Exception as e:
            print(f"  [ERROR] {e} (attempt {attempt+1}/{retries})")
    return False


def main():
    mapping_path = os.path.join(OUTPUT_DIR, "mapping.json")
    with open(mapping_path, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    success = 0
    for recipe_id, name, prompt in MISSING_RECIPES:
        slug = slugify(name)
        filename = f"{slug}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)
        seed = int(hashlib.md5(name.encode("utf-8")).hexdigest()[:8], 16) % 100000

        print(f"Generating: {name} -> {filename}")
        if generate_image(prompt, filepath, seed):
            mapping[recipe_id] = filename
            success += 1
            print(f"  OK: {filename} ({os.path.getsize(filepath)} bytes)")
        else:
            print(f"  FAILED: {name}")

    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"\n完成: 成功 {success}/{len(MISSING_RECIPES)}")
    print(f"mapping.json 共 {len(mapping)} 条")


if __name__ == "__main__":
    main()
