"""
菜谱图片批量生成脚本：调用 Pollinations.ai (flux模型) 为每道菜生成真实食物照片。
每道菜有详细的英文视觉描述，确保图片与菜品一致。
运行方式: python generate_images.py
"""
import os
import time
import hashlib
import urllib.parse
import urllib.request
import json

API_BASE = "http://127.0.0.1:8000/api/v1"
IMG_API = "https://image.pollinations.ai/prompt"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "static", "recipes")

# 菜谱名 -> 精细英文视觉描述（强调成品的真实外观）
DISH_PROMPTS = {
    # ---- 鸡蛋类 ----
    "番茄炒蛋": "A plate of Chinese tomato scrambled eggs, bright red tomato chunks mixed with fluffy golden yellow scrambled eggs, garnished with chopped scallions, on a white ceramic plate, overhead shot, professional food photography, soft natural lighting, appetizing",
    "青椒炒蛋": "A plate of Chinese stir-fried eggs with green peppers, large pieces of lightly charred green bell pepper mixed with golden brown scrambled eggs, on a white plate, overhead view, food photography, appetizing",
    "鸡蛋羹": "A bowl of Chinese steamed egg custard, smooth pale yellow surface like silk, drizzled with soy sauce and sesame oil, sprinkled with chopped scallions, in a white ceramic bowl, close-up, food photography, steaming",
    "黄瓜炒鸡蛋": "A plate of Chinese stir-fried cucumber with eggs, light green cucumber slices mixed with golden egg pieces, on a white plate, overhead view, food photography, home cooking",
    "紫菜蛋花汤": "A bowl of Chinese seaweed egg drop soup, clear broth with dark green seaweed and yellow egg ribbons floating, sprinkled with scallions, in a white bowl, overhead view, food photography",
    "番茄蛋汤": "A bowl of Chinese tomato egg soup, orange-red tomato broth with yellow egg ribbons, sprinkled with scallions, steaming hot, in a white bowl, overhead view, food photography",
    # ---- 主食类 ----
    "蛋炒饭": "A bowl of Chinese egg fried rice, golden yellow rice grains with bits of egg, chopped scallions and diced ham, in a ceramic bowl, overhead view, food photography, appetizing",
    "鸡蛋炒饭": "A plate of Chinese egg fried rice, separate golden rice grains with scrambled egg bits and chopped scallions, on a white plate, overhead view, food photography",
    "西红柿鸡蛋面": "A bowl of Chinese tomato egg noodles, wheat noodles in red tomato soup with egg and scallions, in a large bowl, overhead view, food photography, steaming",
    "番茄鸡蛋面": "A bowl of Chinese tomato egg noodles, noodles in orange-red tomato broth with egg pieces, in a white bowl, overhead view, food photography",
    # ---- 猪肉类 ----
    "红烧肉": "A bowl of Chinese braised pork belly (hongshaorou), glossy dark caramel-colored pork belly chunks glistening, thick brown sauce, in a ceramic bowl, overhead view, food photography, rich and appetizing",
    "糖醋排骨": "A plate of Chinese sweet and sour spare ribs, glossy caramel-colored ribs coated in sticky sweet sauce, sprinkled with sesame seeds, on a white plate, overhead view, food photography",
    "鱼香肉丝": "A plate of Chinese Yu Xiang shredded pork, thin pork strips with wood ear mushrooms, bamboo shoots and carrots in reddish-brown sauce, on a white plate, overhead view, food photography",
    "回锅肉": "A plate of Chinese twice-cooked pork, thin slices of pork belly with green peppers and garlic sprouts in dark red chili sauce, on a white plate, overhead view, food photography",
    "青椒肉丝": "A plate of Chinese stir-fried shredded pork with green peppers, thin pork strips with green pepper strips in light brown sauce, on a white plate, overhead view, food photography",
    "肉末茄子": "A plate of Chinese eggplant with minced pork, soft purple eggplant pieces coated in brown meat sauce, on a white plate, overhead view, food photography",
    "肉末豆腐": "A bowl of Chinese tofu with minced pork, white soft tofu cubes in brown meat sauce, sprinkled with scallions, in a ceramic bowl, overhead view, food photography",
    "黄瓜炒肉片": "A plate of Chinese stir-fried sliced pork with cucumber, pork slices with green cucumber pieces, on a white plate, overhead view, food photography",
    "蒜薹炒肉": "A plate of Chinese stir-fried pork with garlic sprouts, green garlic sprouts with pork slices in brown sauce, on a white plate, overhead view, food photography",
    "木须肉": "A plate of Chinese Moo Shu pork, sliced pork with scrambled egg, wood ear mushrooms and cucumber, in a light brown sauce, on a white plate, overhead view, food photography",
    # ---- 牛肉类 ----
    "青椒炒牛肉": "A plate of Chinese stir-fried beef with green peppers, tender beef slices with green bell pepper strips in brown sauce, on a white plate, overhead view, food photography",
    "番茄牛腩": "A bowl of Chinese beef brisket with tomatoes, soft beef chunks in red tomato sauce with potato pieces, in a ceramic bowl, overhead view, food photography",
    "芹菜炒牛肉": "A plate of Chinese stir-fried beef with celery, beef slices with green celery sticks in brown sauce, on a white plate, overhead view, food photography",
    "洋葱炒牛肉": "A plate of Chinese stir-fried beef with onions, beef slices with onion strips in brown sauce, on a white plate, overhead view, food photography",
    "土豆烧牛肉": "A plate of Chinese braised beef with potatoes, beef chunks and potato cubes in dark brown sauce, on a white plate, overhead view, food photography",
    "西红柿炖牛腩": "A bowl of Chinese beef brisket stew with tomatoes, tender beef chunks and carrot pieces in rich red tomato broth, in a ceramic bowl, overhead view, food photography",
    "葱爆羊肉": "A plate of Chinese stir-fried lamb with scallions, thin lamb slices with large scallion sections in brown sauce, on a white plate, overhead view, food photography",
    # ---- 鸡肉类 ----
    "宫保鸡丁": "A plate of Chinese Kung Pao chicken, diced chicken with peanuts and dried chilies in glossy reddish sauce, on a white plate, overhead view, food photography, appetizing",
    "可乐鸡翅": "A plate of Chinese cola chicken wings, glossy dark brown caramel-colored chicken wings glazed with sweet sauce, on a white plate, overhead view, food photography",
    "白切鸡": "A plate of Chinese white-cut chicken, pale bone-in chicken pieces neatly arranged, with a small dish of ginger scallion oil dip, on a white plate, overhead view, food photography",
    # ---- 海鲜类 ----
    "清蒸鱼": "A whole Chinese steamed fish on a large white plate, whole fish with soy sauce, shredded ginger and scallion on top, garnished with cilantro, overhead view, professional food photography, restaurant presentation",
    "酸菜鱼": "A large bowl of Chinese Sichuan boiled fish with pickled cabbage, white fish slices in yellow-green pickled cabbage broth, sprinkled with dried chilies, overhead view, food photography, steaming",
    "蒜蓉虾": "A plate of Chinese garlic shrimp, whole shrimp with heads on, topped with golden minced garlic, on a white plate, overhead view, food photography, appetizing",
    "炒虾仁": "A plate of Chinese stir-fried shrimp, pink curled shrimp with diced cucumber and carrot, on a white plate, overhead view, food photography",
    "西兰花炒虾仁": "A plate of Chinese stir-fried shrimp with broccoli, green broccoli florets and pink shrimp, on a white plate, overhead view, food photography",
    "蒜蓉粉丝蒸虾": "A plate of Chinese steamed shrimp with garlic and vermicelli, shrimp opened flat on glass noodles with golden garlic, on a white plate, overhead view, food photography",
    "番茄龙利鱼": "A plate of Chinese tomato fish, white fish fillets in red tomato sauce, on a white plate, overhead view, food photography",
    # ---- 三文鱼系列 ----
    "香煎三文鱼": "A plate of pan-seared salmon fillet, golden crispy skin side up, pink-orange salmon flesh, with a lemon wedge, on a white plate, overhead view, food photography, appetizing",
    "三文鱼炒饭": "A bowl of salmon fried rice, golden rice with pink salmon cubes, egg bits and scallions, in a ceramic bowl, overhead view, food photography",
    "蒜香三文鱼": "A plate of Chinese garlic salmon, salmon chunks with golden minced garlic, on a white plate, overhead view, food photography",
    "三文鱼头豆腐汤": "A bowl of Chinese salmon head tofu soup, milky white broth with fish head pieces and white tofu cubes, sprinkled with scallions, in a ceramic bowl, overhead view, food photography",
    "三文鱼刺身": "A plate of salmon sashimi, thin slices of raw salmon arranged neatly, orange-pink flesh with white fat lines, on a dark plate with wasabi and soy sauce, overhead view, food photography",
    # ---- 豆腐/豆制品 ----
    "麻婆豆腐": "A bowl of Chinese Mapo tofu, white soft tofu cubes in bright red chili oil sauce with minced meat, sprinkled with Sichuan peppercorn powder and scallions, in a ceramic bowl, overhead view, food photography",
    # ---- 素菜类 ----
    "土豆丝": "A plate of Chinese stir-fried shredded potatoes, thin white potato strips with red chili and green scallion, on a white plate, overhead view, food photography",
    "炒土豆丝": "A plate of Chinese stir-fried shredded potatoes with vinegar, thin golden-white potato strips, on a white plate, overhead view, food photography",
    "青椒土豆丝": "A plate of Chinese stir-fried shredded potatoes with green peppers, white potato strips with green pepper strips, on a white plate, overhead view, food photography",
    "炒青菜": "A plate of Chinese stir-fried green vegetables, bright green bok choy with garlic, on a white plate, overhead view, food photography",
    "蒜蓉西兰花": "A plate of Chinese stir-fried broccoli with garlic, bright green broccoli florets, on a white plate, overhead view, food photography",
    "蚝油生菜": "A plate of Chinese lettuce with oyster sauce, green lettuce leaves with glossy dark brown sauce drizzled on top, on a white plate, overhead view, food photography",
    "凉拌黄瓜": "A plate of Chinese cold cucumber salad, green cucumber chunks smashed with garlic and chili oil, on a white plate, overhead view, food photography",
    "凉拌番茄": "A plate of Chinese sliced tomato salad, red tomato slices sprinkled with white sugar, on a white plate, overhead view, food photography",
    "醋溜白菜": "A plate of Chinese stir-fried cabbage with vinegar, white-yellow cabbage pieces with red chili, on a white plate, overhead view, food photography",
    "干煸四季豆": "A plate of Chinese dry-fried green beans, wrinkled green beans with minced pork and dried chilies, on a white plate, overhead view, food photography",
    "鱼香茄子": "A plate of Chinese fish-fragrant eggplant, soft purple eggplant strips in reddish-brown sauce with minced meat, on a white plate, overhead view, food photography",
    "地三鲜": "A plate of Chinese Di San Xian, fried potato eggplant and green pepper pieces in brown sauce, on a white plate, overhead view, food photography",
    # ---- 汤类 ----
    "酸辣汤": "A bowl of Chinese hot and sour soup, dark brown thickened broth with tofu strips, wood ear mushrooms and egg ribbons, in a white bowl, overhead view, food photography",
    # ---- 排骨类 ----
    "清蒸排骨": "A plate of Chinese steamed pork ribs, pale pork rib pieces with black bean sauce and scallion, on a white plate, overhead view, food photography",
}


def fetch_recipes():
    """从后端 API 获取所有菜谱"""
    with urllib.request.urlopen(f"{API_BASE}/recipes") as resp:
        return json.loads(resp.read().decode("utf-8"))


def generate_image(prompt: str, output_path: str, seed: int) -> bool:
    """调用 Pollinations.ai flux 模型生成图片"""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{IMG_API}/{encoded_prompt}?width=512&height=512&nologo=true&seed={seed}&model=flux"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=180) as resp:
            if resp.status == 200 and "image" in resp.headers.get("Content-Type", ""):
                data = resp.read()
                if len(data) > 2000:  # 确保不是空白/损坏图片
                    with open(output_path, "wb") as f:
                        f.write(data)
                    return True
                else:
                    print(f"  [WARN] Image too small: {len(data)} bytes")
                    return False
            else:
                print(f"  [WARN] status={resp.status}, type={resp.headers.get('Content-Type')}")
                return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def slugify(name: str) -> str:
    """菜谱名 -> 文件名 slug"""
    return hashlib.md5(name.encode("utf-8")).hexdigest()[:12]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    recipes = fetch_recipes()
    print(f"共 {len(recipes)} 道菜谱，使用 flux 模型生成图片...\n")

    mapping_path = os.path.join(OUTPUT_DIR, "mapping.json")
    mapping = {}

    success = 0
    for i, recipe in enumerate(recipes):
        name = recipe["name"]
        recipe_id = recipe["id"]
        slug = slugify(name)
        filename = f"{slug}.jpg"
        filepath = os.path.join(OUTPUT_DIR, filename)

        prompt = DISH_PROMPTS.get(name)
        if not prompt:
            prompt = f"A plate of Chinese home cooking dish, served on a white ceramic plate, overhead view, professional food photography, soft natural lighting, appetizing"

        seed = int(hashlib.md5(name.encode("utf-8")).hexdigest()[:8], 16) % 100000

        print(f"[{i+1}/{len(recipes)}] {name}", flush=True)
        if generate_image(prompt, filepath, seed):
            mapping[recipe_id] = filename
            success += 1
            print(f"  -> {filename} ({os.path.getsize(filepath)} bytes)", flush=True)
        else:
            print(f"  -> FAILED", flush=True)

        time.sleep(0.3)

    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    failed = len(recipes) - success
    print(f"\n完成: 成功 {success}, 失败 {failed}")
    print(f"映射已保存到: {mapping_path}")


if __name__ == "__main__":
    main()
