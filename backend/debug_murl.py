# 检查 murl 实际格式
import re
import httpx

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

url = "https://www.bing.com/images/search?q=beef+stir+fry&form=HDRSC2"
r = httpx.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
text = r.text

# find first occurrence of murl
idx = text.find("murl")
print("context around first murl:")
print(repr(text[idx-20:idx+200]))
print()
# try multiple regex patterns
patterns = [
    r'"murl":"(https?://[^"]+)"',
    r'murl&quot;:&quot;(https?://[^&]+)&',
    r'murl=([^&"]+)',
    r'"murl":"([^,]+)"',
    r'murl":"([^"]+)"',
]
for p in patterns:
    m = re.findall(p, text)
    print(f"pattern {p!r}: {len(m)} matches")
    if m:
        print(f"  first: {m[0][:120]}")
