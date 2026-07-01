# 调试 Bing 图片搜索响应格式
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

url = "https://www.bing.com/images/search?q=beef+stir+fry&form=HDRSC2"
r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
print("status:", r.status_code)
print("len:", len(r.text))
# show snippet containing 'murl' or 'images.unsplash'
import re
for kw in ["murl", "images.unsplash", "images.pexels", "mediaurl", "imgurl", "purl"]:
    cnt = r.text.count(kw)
    print(f"  {kw}: {cnt}")
# save first 3000 chars
with open("bing_sample.html", "w", encoding="utf-8") as f:
    f.write(r.text[:5000])
print("saved sample")
