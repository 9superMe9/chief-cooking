"""
生成交互式 HTML 演示文件：从后端 API 获取全部菜谱数据，嵌入到自包含 HTML 中。
运行方式: python build_demo.py
输出: demo.html
"""
import json
import urllib.request

API_BASE = "http://127.0.0.1:8000/api/v1"
OUTPUT = "demo.html"

# 食材分类（用于交互式选择界面）
INGREDIENT_CATEGORIES = {
    "肉禽蛋": ["鸡蛋", "猪肉", "排骨", "牛肉", "鸡肉", "鸡翅", "羊肉", "虾仁", "虾"],
    "水产海鲜": ["三文鱼", "鱼", "龙利鱼", "酸菜鱼"],
    "蔬菜": ["番茄", "青椒", "黄瓜", "土豆", "西兰花", "生菜", "白菜", "茄子", "四季豆", "蒜薹", "芹菜", "洋葱", "紫菜", "胡萝卜", "蘑菇", "豆腐"],
    "主食其他": ["米饭", "面条", "粉丝", "葱", "蒜", "姜"],
}

# 用于演示 AI 动态生成的"新食材"
NOVEL_INGREDIENTS = ["牛油果", "秋葵", "芝士", "咖喱"]


def fetch_recipes():
    with urllib.request.urlopen(f"{API_BASE}/recipes") as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_html(recipes):
    recipes_json = json.dumps(recipes, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>饭点小厨 · AI 驱动的智能菜谱推荐助手</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --primary:#FF6B35;--secondary:#F7931E;--accent:#2EC4B6;--dark:#1A1A2E;
  --light:#FFF8F0;--gray:#F5F0EB;--text:#333;--text-light:#666;
  --radius:16px;--shadow:0 4px 20px rgba(0,0,0,.08);
}}
body{{font-family:'-apple-system','Segoe UI','Microsoft YaHei',sans-serif;background:var(--light);color:var(--text);line-height:1.6;overflow-x:hidden}}

/* Hero */
.hero{{min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;
  background:linear-gradient(135deg,#FF6B35 0%,#F7931E 40%,#FFB627 100%);color:#fff;text-align:center;padding:2rem;position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;top:-50%;left:-50%;width:200%;height:200%;
  background:radial-gradient(circle,rgba(255,255,255,.1) 0%,transparent 60%);animation:rotate 20s linear infinite}}
@keyframes rotate{{to{{transform:rotate(360deg)}}}}
.hero h1{{font-size:4rem;font-weight:800;margin-bottom:.5rem;z-index:1;text-shadow:0 2px 10px rgba(0,0,0,.2)}}
.hero .tagline{{font-size:1.4rem;opacity:.95;margin-bottom:2rem;z-index:1}}
.hero .badges{{display:flex;flex-wrap:wrap;gap:.6rem;justify-content:center;margin-bottom:2.5rem;z-index:1}}
.hero .badge{{background:rgba(255,255,255,.2);backdrop-filter:blur(10px);padding:.5rem 1.2rem;border-radius:30px;font-size:.85rem;border:1px solid rgba(255,255,255,.3)}}
.hero .cta{{display:flex;gap:1rem;z-index:1}}
.hero .btn{{background:#fff;color:var(--primary);padding:.9rem 2rem;border-radius:30px;text-decoration:none;font-weight:700;font-size:1rem;transition:transform .2s,box-shadow .2s;cursor:pointer;border:none}}
.hero .btn:hover{{transform:translateY(-3px);box-shadow:0 8px 25px rgba(0,0,0,.2)}}
.hero .btn.outline{{background:transparent;color:#fff;border:2px solid #fff}}
.hero .scroll-hint{{position:absolute;bottom:2rem;font-size:.8rem;opacity:.7;animation:bounce 2s infinite;z-index:1}}
@keyframes bounce{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-8px)}}}}

/* Section */
.section{{max-width:1200px;margin:0 auto;padding:5rem 2rem}}
.section h2{{font-size:2.2rem;font-weight:800;text-align:center;margin-bottom:.5rem;color:var(--dark)}}
.section .subtitle{{text-align:center;color:var(--text-light);margin-bottom:3rem;font-size:1.05rem}}

/* Architecture */
.arch{{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:1rem;margin-top:2rem}}
.arch-node{{background:#fff;padding:1.5rem 2rem;border-radius:var(--radius);box-shadow:var(--shadow);text-align:center;min-width:140px;transition:transform .2s}}
.arch-node:hover{{transform:translateY(-4px)}}
.arch-node .icon{{font-size:2rem;margin-bottom:.5rem}}
.arch-node .title{{font-weight:700;font-size:.95rem;margin-bottom:.2rem}}
.arch-node .desc{{font-size:.75rem;color:var(--text-light)}}
.arch-arrow{{font-size:1.8rem;color:var(--primary);font-weight:bold}}

/* Demo */
.demo-container{{background:#fff;border-radius:var(--radius);box-shadow:var(--shadow);overflow:hidden;margin-top:1rem}}
.demo-tabs{{display:flex;border-bottom:2px solid var(--gray)}}
.demo-tab{{flex:1;padding:1.2rem;text-align:center;cursor:pointer;font-weight:600;color:var(--text-light);transition:all .2s;border-bottom:3px solid transparent}}
.demo-tab.active{{color:var(--primary);border-bottom-color:var(--primary);background:var(--light)}}
.demo-tab .tab-icon{{font-size:1.5rem;display:block;margin-bottom:.3rem}}
.demo-panel{{padding:2rem;display:none}}
.demo-panel.active{{display:block;animation:fadeIn .3s}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(10px)}}to{{opacity:1;transform:translateY(0)}}}}

/* Ingredient selector */
.ing-categories{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1.5rem;margin-bottom:2rem}}
.ing-category h4{{font-size:.9rem;color:var(--text-light);margin-bottom:.6rem;text-transform:uppercase;letter-spacing:.5px}}
.ing-chips{{display:flex;flex-wrap:wrap;gap:.5rem}}
.ing-chip{{padding:.4rem .9rem;border-radius:20px;border:2px solid #E0D5C8;background:#fff;cursor:pointer;font-size:.85rem;transition:all .15s;user-select:none}}
.ing-chip:hover{{border-color:var(--primary)}}
.ing-chip.selected{{background:var(--primary);color:#fff;border-color:var(--primary)}}
.novel-chip{{padding:.4rem .9rem;border-radius:20px;border:2px dashed var(--accent);background:#E8F8F5;cursor:pointer;font-size:.85rem;color:var(--accent);user-select:none}}
.novel-chip.selected{{background:var(--accent);color:#fff;border-style:solid}}

.demo-actions{{display:flex;gap:1rem;align-items:center;margin:1.5rem 0;flex-wrap:wrap}}
.btn-primary{{background:var(--primary);color:#fff;padding:.8rem 2rem;border-radius:30px;border:none;font-size:1rem;font-weight:600;cursor:pointer;transition:transform .2s}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 6px 15px rgba(255,107,53,.4)}}
.btn-primary:active{{transform:translateY(0)}}
.btn-secondary{{background:var(--accent);color:#fff;padding:.8rem 2rem;border-radius:30px;border:none;font-size:1rem;font-weight:600;cursor:pointer}}
.selected-display{{font-size:.9rem;color:var(--text-light)}}
.selected-display strong{{color:var(--primary)}}

/* Recipe cards */
.recipe-results{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.5rem;margin-top:1.5rem}}
.recipe-card{{background:#fff;border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);transition:transform .2s,box-shadow .2s;cursor:pointer}}
.recipe-card:hover{{transform:translateY(-4px);box-shadow:0 8px 30px rgba(0,0,0,.12)}}
.recipe-card img{{width:100%;height:180px;object-fit:cover;background:var(--gray)}}
.recipe-card .info{{padding:1rem}}
.recipe-card .name{{font-size:1.1rem;font-weight:700;margin-bottom:.3rem}}
.recipe-card .desc{{font-size:.85rem;color:var(--text-light);margin-bottom:.6rem;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.recipe-card .meta{{display:flex;gap:.8rem;font-size:.75rem;color:var(--text-light)}}
.recipe-card .meta span{{background:var(--gray);padding:.2rem .6rem;border-radius:10px}}
.matched{{color:var(--accent);font-weight:600}}
.missing{{color:#E74C3C;font-size:.8rem}}
.ai-tag{{display:inline-block;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:.2rem .6rem;border-radius:10px;font-size:.7rem;margin-bottom:.5rem}}
.reason{{font-size:.82rem;color:var(--primary);font-style:italic;margin-top:.5rem;padding:.5rem;background:#FFF5F0;border-radius:8px;border-left:3px solid var(--primary)}}
.loading{{text-align:center;padding:3rem;color:var(--text-light)}}
.loading .spinner{{display:inline-block;width:40px;height:40px;border:4px solid var(--gray);border-top-color:var(--primary);border-radius:50%;animation:spin .8s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}

/* Gallery */
.gallery-filters{{display:flex;gap:.5rem;justify-content:center;flex-wrap:wrap;margin-bottom:2rem}}
.gallery-filter{{padding:.5rem 1.2rem;border-radius:20px;border:2px solid #E0D5C8;background:#fff;cursor:pointer;font-size:.85rem;transition:all .15s}}
.gallery-filter.active{{background:var(--dark);color:#fff;border-color:var(--dark)}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:1rem}}
.gallery-item{{background:#fff;border-radius:12px;overflow:hidden;box-shadow:var(--shadow);transition:transform .2s;cursor:pointer}}
.gallery-item:hover{{transform:scale(1.05)}}
.gallery-item img{{width:100%;height:140px;object-fit:cover;background:var(--gray)}}
.gallery-item .g-name{{padding:.6rem;font-size:.85rem;font-weight:600;text-align:center}}
.gallery-item .g-emoji{{font-size:3rem;text-align:center;padding:2rem 0;background:var(--gray)}}

/* Features */
.features{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:2rem;margin-top:2rem}}
.feature{{background:#fff;padding:2.5rem;border-radius:var(--radius);box-shadow:var(--shadow);text-align:center;transition:transform .2s}}
.feature:hover{{transform:translateY(-6px)}}
.feature .f-icon{{font-size:3rem;margin-bottom:1rem}}
.feature h3{{font-size:1.3rem;margin-bottom:.8rem;color:var(--dark)}}
.feature p{{color:var(--text-light);font-size:.92rem;line-height:1.7}}
.feature .tech{{margin-top:1rem;font-size:.78rem;color:var(--accent);font-weight:600}}

/* Modal */
.modal-overlay{{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);display:none;align-items:center;justify-content:center;z-index:999;padding:2rem}}
.modal-overlay.show{{display:flex}}
.modal{{background:#fff;border-radius:var(--radius);max-width:600px;width:100%;max-height:85vh;overflow-y:auto}}
.modal-header{{padding:1.5rem;border-bottom:1px solid var(--gray);display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;background:#fff;z-index:1}}
.modal-header h3{{font-size:1.4rem}}
.modal-close{{background:none;border:none;font-size:1.5rem;cursor:pointer;color:var(--text-light);padding:.5rem}}
.modal-body{{padding:1.5rem}}
.modal-body img{{width:100%;height:250px;object-fit:cover;border-radius:12px;margin-bottom:1rem;background:var(--gray)}}
.modal-body .section-label{{font-weight:700;margin:1rem 0 .3rem;color:var(--dark)}}
.modal-body .ingredients-list{{display:flex;flex-wrap:wrap;gap:.4rem}}
.modal-body .ing-tag{{padding:.3rem .8rem;border-radius:12px;font-size:.8rem}}
.modal-body .ing-tag.have{{background:#D4F1F1;color:var(--accent)}}
.modal-body .ing-tag.miss{{background:#FDEAEA;color:#E74C3C}}
.modal-body .steps{{counter-reset:step}}
.modal-body .step{{display:flex;gap:.8rem;margin-bottom:.8rem;align-items:flex-start}}
.modal-body .step::before{{counter-increment:step;content:counter(step);background:var(--primary);color:#fff;width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:700;flex-shrink:0;margin-top:2px}}

/* Tech section */
.tech-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1rem;margin-top:2rem}}
.tech-item{{background:#fff;padding:1.5rem;border-radius:12px;text-align:center;box-shadow:var(--shadow)}}
.tech-item .t-icon{{font-size:2rem;margin-bottom:.5rem}}
.tech-item .t-name{{font-weight:700;font-size:.9rem}}
.tech-item .t-desc{{font-size:.75rem;color:var(--text-light);margin-top:.3rem}}

/* TRAE journey */
.journey{{position:relative;padding-left:2rem;margin-top:2rem}}
.journey::before{{content:'';position:absolute;left:8px;top:0;bottom:0;width:2px;background:linear-gradient(to bottom,var(--primary),var(--accent))}}
.journey-item{{position:relative;margin-bottom:2rem;padding-bottom:.5rem}}
.journey-item::before{{content:'';position:absolute;left:-30px;top:4px;width:16px;height:16px;border-radius:50%;background:var(--primary);border:3px solid #fff;box-shadow:0 0 0 2px var(--primary)}}
.journey-item h4{{font-size:1.1rem;margin-bottom:.3rem;color:var(--dark)}}
.journey-item .date{{font-size:.8rem;color:var(--accent);font-weight:600;margin-bottom:.3rem}}
.journey-item p{{font-size:.9rem;color:var(--text-light)}}

/* Footer */
.footer{{background:var(--dark);color:rgba(255,255,255,.7);text-align:center;padding:3rem 2rem;margin-top:3rem}}
.footer h3{{color:#fff;margin-bottom:.5rem}}
.footer a{{color:var(--secondary);text-decoration:none}}

/* Responsive */
@media(max-width:768px){{
  .hero h1{{font-size:2.5rem}}
  .hero .tagline{{font-size:1rem}}
  .arch{{flex-direction:column}}
  .arch-arrow{{transform:rotate(90deg)}}
  .section{{padding:3rem 1rem}}
}}
</style>
</head>
<body>

<!-- Hero -->
<section class="hero">
  <h1>🍳 饭点小厨</h1>
  <p class="tagline">AI 驱动的智能菜谱推荐助手 · 让每一餐都有灵感</p>
  <div class="badges">
    <span class="badge">🚀 FastAPI</span>
    <span class="badge">📱 uni-app H5</span>
    <span class="badge">🧠 阿里云百炼 Qwen3.7-Plus</span>
    <span class="badge">🎨 Pollinations.ai Flux</span>
    <span class="badge">✨ 58 道菜谱 · AI 动态生成</span>
  </div>
  <div class="cta">
    <button class="btn" onclick="document.getElementById('demo').scrollIntoView({{behavior:'smooth'}})">🎬 立即体验</button>
    <button class="btn outline" onclick="document.getElementById('features').scrollIntoView({{behavior:'smooth'}})">了解功能</button>
  </div>
  <div class="scroll-hint">↓ 向下滚动探索</div>
</section>

<!-- Architecture -->
<section class="section" id="arch">
  <h2>🏗️ 技术架构</h2>
  <p class="subtitle">前后端分离 · AI 赋能 · 全链路智能推荐</p>
  <div class="arch">
    <div class="arch-node"><div class="icon">👤</div><div class="title">用户</div><div class="desc">拍照/选食材</div></div>
    <div class="arch-arrow">→</div>
    <div class="arch-node"><div class="icon">📱</div><div class="title">前端 H5</div><div class="desc">uni-app 跨端</div></div>
    <div class="arch-arrow">→</div>
    <div class="arch-node"><div class="icon">⚡</div><div class="title">FastAPI</div><div class="desc">异步后端</div></div>
    <div class="arch-arrow">→</div>
    <div class="arch-node"><div class="icon">🧠</div><div class="title">AI 百炼</div><div class="desc">Qwen3.7-Plus</div></div>
    <div class="arch-arrow">→</div>
    <div class="arch-node"><div class="icon">🎨</div><div class="title">图片生成</div><div class="desc">Flux 模型</div></div>
  </div>
</section>

<!-- Interactive Demo -->
<section class="section" id="demo">
  <h2>🎬 交互演示</h2>
  <p class="subtitle">选择你现有的食材，体验 AI 智能推荐</p>
  <div class="demo-container">
    <div class="demo-tabs">
      <div class="demo-tab active" onclick="switchTab('recommend')"><span class="tab-icon">🥘</span>智能推荐</div>
      <div class="demo-tab" onclick="switchTab('ai-gen')"><span class="tab-icon">✨</span>AI 动态生成</div>
      <div class="demo-tab" onclick="switchTab('gallery')"><span class="tab-icon">📖</span>菜谱库</div>
    </div>

    <!-- Tab 1: Recommend -->
    <div class="demo-panel active" id="panel-recommend">
      <div class="ing-categories" id="ing-categories"></div>
      <div class="demo-actions">
        <button class="btn-primary" onclick="recommend()">🔍 智能推荐菜谱</button>
        <button class="btn-secondary" onclick="clearSelection()">清空选择</button>
        <span class="selected-display">已选 <strong id="sel-count">0</strong> 种食材</span>
      </div>
      <div id="recommend-results"></div>
    </div>

    <!-- Tab 2: AI Generate -->
    <div class="demo-panel" id="panel-ai-gen">
      <div style="background:#E8F8F5;padding:1.5rem;border-radius:12px;margin-bottom:1.5rem">
        <h4 style="color:var(--accent);margin-bottom:.5rem">✨ AI 动态菜谱生成</h4>
        <p style="font-size:.88rem;color:var(--text-light)">当菜谱库中没有足够匹配的菜谱时，AI 会根据你的食材<span style="color:var(--accent);font-weight:600">实时生成全新菜谱</span>。试试选择一些不常见的食材：</p>
      </div>
      <div class="ing-chips" style="margin-bottom:1.5rem">
        <span class="novel-chip" onclick="toggleNovel(this)">🥑 牛油果</span>
        <span class="novel-chip" onclick="toggleNovel(this)">🌿 秋葵</span>
        <span class="novel-chip" onclick="toggleNovel(this)">🧀 芝士</span>
        <span class="novel-chip" onclick="toggleNovel(this)">🍛 咖喱</span>
      </div>
      <div class="demo-actions">
        <button class="btn-primary" onclick="aiGenerate()" style="background:linear-gradient(135deg,#667eea,#764ba2)">✨ AI 生成菜谱</button>
        <span class="selected-display">选择食材后点击生成</span>
      </div>
      <div id="ai-results"></div>
    </div>

    <!-- Tab 3: Gallery -->
    <div class="demo-panel" id="panel-gallery">
      <div class="gallery-filters" id="gallery-filters"></div>
      <div class="gallery" id="gallery-grid"></div>
    </div>
  </div>
</section>

<!-- Features -->
<section class="section" id="features" style="background:var(--gray)">
  <h2>💡 核心功能</h2>
  <p class="subtitle">三大 AI 能力，打造智能化烹饪体验</p>
  <div class="features">
    <div class="feature">
      <div class="f-icon">📸</div>
      <h3>AI 拍照识食材</h3>
      <p>拍照上传冰箱食材，AI 多模态模型自动识别，免去手动输入烦恼。支持多种常见食材的同时识别，准确率高。</p>
      <div class="tech">Qwen3.7-Plus 多模态 · 图片识别</div>
    </div>
    <div class="feature">
      <div class="f-icon">🧠</div>
      <h3>智能菜谱推荐</h3>
      <p>基于核心食材覆盖率评分算法，结合随机扰动与候选池抽样，每次推荐都有不同组合。支持"几菜几汤"自定义需求。</p>
      <div class="tech">评分算法 ±15 扰动 · Top N×2 候选池</div>
    </div>
    <div class="feature">
      <div class="f-icon">✨</div>
      <h3>AI 动态菜谱生成</h3>
      <p>当菜谱库匹配不足 3 道时，AI 根据你的食材实时生成全新菜谱。10 分钟内相同组合不重复生成，1 小时后自动清理。</p>
      <div class="tech">Qwen3.7-Plus · 10min 缓存 · 自动清理</div>
    </div>
  </div>
</section>

<!-- Tech Stack -->
<section class="section" id="tech">
  <h2>🛠️ 技术栈</h2>
  <p class="subtitle">现代化全栈技术方案</p>
  <div class="tech-grid">
    <div class="tech-item"><div class="t-icon">⚡</div><div class="t-name">FastAPI</div><div class="t-desc">异步后端框架</div></div>
    <div class="tech-item"><div class="t-icon">📱</div><div class="t-name">uni-app</div><div class="t-desc">跨端前端 H5</div></div>
    <div class="tech-item"><div class="t-icon">🗄️</div><div class="t-name">SQLAlchemy</div><div class="t-desc">异步 ORM</div></div>
    <div class="tech-item"><div class="t-icon">🧠</div><div class="t-name">Qwen3.7-Plus</div><div class="t-desc">阿里云百炼 AI</div></div>
    <div class="tech-item"><div class="t-icon">🎨</div><div class="t-name">Pollinations</div><div class="t-desc">Flux 图片生成</div></div>
    <div class="tech-item"><div class="t-icon">🔒</div><div class="t-name">JWT</div><div class="t-desc">用户认证</div></div>
    <div class="tech-item"><div class="t-icon">📊</div><div class="t-name">Token 追踪</div><div class="t-desc">用量监控预警</div></div>
    <div class="tech-item"><div class="t-icon">🌐</div><div class="t-name">Cloudflare</div><div class="t-desc">Tunnel 公网访问</div></div>
  </div>
</section>

<!-- TRAE Journey -->
<section class="section" id="journey" style="background:var(--gray)">
  <h2>🚀 TRAE 实践过程</h2>
  <p class="subtitle">从需求到上线的完整开发旅程</p>
  <div class="journey">
    <div class="journey-item">
      <div class="date">阶段一 · 基础搭建</div>
      <h4>项目初始化与后端框架</h4>
      <p>使用 Trae IDE 搭建 FastAPI 异步后端，设计数据库模型（用户/食材/菜谱/推荐），完成基础 CRUD API 和 JWT 认证。</p>
    </div>
    <div class="journey-item">
      <div class="date">阶段二 · AI 集成</div>
      <h4>阿里云百炼多模态接入</h4>
      <p>集成 Qwen3.7-Plus 多模态模型，实现拍照识别食材、AI 推荐理由润色、烹饪步骤增强。建立 Token 用量追踪与 80% 预警机制。</p>
    </div>
    <div class="journey-item">
      <div class="date">阶段三 · 推荐优化</div>
      <h4>智能推荐算法迭代</h4>
      <p>核心食材覆盖率评分 + ±15 随机扰动 + Top N×2 候选池抽样，解决推荐结果重复问题。补充 5 道三文鱼菜谱修复推荐缺失。</p>
    </div>
    <div class="journey-item">
      <div class="date">阶段四 · AI 动态生成</div>
      <h4>混合推荐策略上线</h4>
      <p>固定菜谱库 58 道 + AI 动态生成无限覆盖。10 分钟缓存防重复，1 小时自动清理。AI 生成菜谱标记 <code>__AI_GENERATED__</code>。</p>
    </div>
  </div>
</section>

<!-- Footer -->
<footer class="footer">
  <h3>🍳 饭点小厨</h3>
  <p>AI 驱动的智能菜谱推荐助手 · Trae AI 大赛参赛作品</p>
  <p style="margin-top:.5rem;font-size:.85rem">FastAPI + uni-app + 阿里云百炼 Qwen3.7-Plus + Pollinations.ai Flux</p>
</footer>

<!-- Modal -->
<div class="modal-overlay" id="modal" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <div class="modal-header">
      <h3 id="modal-title"></h3>
      <button class="modal-close" onclick="closeModal()">✕</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>

<script>
// 菜谱数据
const RECIPES = {recipes_json};

// 食材分类
const ING_CATEGORIES = {json.dumps(INGREDIENT_CATEGORIES, ensure_ascii=False)};

// 后端地址（用于加载图片）
const BACKEND_URL = window.location.origin;

// 状态
let selectedIngredients = new Set();
let selectedNovel = new Set();

// 初始化食材选择区
function initIngredients() {{
  const container = document.getElementById('ing-categories');
  container.innerHTML = '';
  for (const [cat, ings] of Object.entries(ING_CATEGORIES)) {{
    const div = document.createElement('div');
    div.className = 'ing-category';
    div.innerHTML = `<h4>${{cat}}</h4><div class="ing-chips">${{
      ings.map(i => `<span class="ing-chip" onclick="toggleIngredient(this,'${{i}}')">${{i}}</span>`).join('')
    }}</div>`;
    container.appendChild(div);
  }}
}}

function toggleIngredient(el, ing) {{
  if (selectedIngredients.has(ing)) {{
    selectedIngredients.delete(ing);
    el.classList.remove('selected');
  }} else {{
    selectedIngredients.add(ing);
    el.classList.add('selected');
  }}
  updateSelCount();
}}

function toggleNovel(el) {{
  const ing = el.textContent.replace(/^[^a-zA-Z\\u4e00-\\u9fa5]+/, '');
  if (selectedNovel.has(ing)) {{
    selectedNovel.delete(ing);
    el.classList.remove('selected');
  }} else {{
    selectedNovel.add(ing);
    el.classList.add('selected');
  }}
}}

function updateSelCount() {{
  document.getElementById('sel-count').textContent = selectedIngredients.size;
}}

function clearSelection() {{
  selectedIngredients.clear();
  document.querySelectorAll('.ing-chip.selected').forEach(el => el.classList.remove('selected'));
  updateSelCount();
  document.getElementById('recommend-results').innerHTML = '';
}}

// 核心食材判断（与后端逻辑一致）
function isCoreIngredient(ing) {{
  const nonCore = ['葱','葱花','葱叶','葱白','蒜','蒜末','蒜片','姜','姜片','姜丝','温水','热水','凉水','盐','糖','酱油','生抽','老抽','醋','料酒','蚝油','淀粉','食用油','油','芝麻油','香油','胡椒粉','花椒粉','辣椒粉','白胡椒粉','味精','鸡精','豆瓣酱','甜面酱','番茄酱','芝麻','白芝麻'];
  for (const nc of nonCore) {{
    if (ing.includes(nc)) return false;
  }}
  return true;
}}

function normalizeIng(ing) {{
  return ing.trim().toLowerCase();
}}

// 推荐算法（简化版，与后端评分逻辑一致）
function recommend() {{
  const ings = Array.from(selectedIngredients);
  if (ings.length === 0) {{
    document.getElementById('recommend-results').innerHTML = '<p style="text-align:center;color:var(--text-light);padding:2rem">请先选择食材 🥬</p>';
    return;
  }}

  const normUserIngs = new Set(ings.map(normalizeIng));
  let scored = [];

  for (const recipe of RECIPES) {{
    const normRecipeIngs = (recipe.ingredients || []).map(normalizeIng);
    const matched = normRecipeIngs.filter(i => normUserIngs.has(i));
    const coreIngs = normRecipeIngs.filter(isCoreIngredient);
    const missing = coreIngs.filter(i => !normUserIngs.has(i));
    const matchedCore = coreIngs.filter(i => normUserIngs.has(i));

    if (matched.length === 0) continue;

    // 核心食材覆盖率评分
    const coreRatio = coreIngs.length > 0 ? matchedCore.length / coreIngs.length : 1;
    const totalRatio = matched.length / normRecipeIngs.length;
    let score = coreRatio * 70 + totalRatio * 30;
    // 随机扰动 ±15
    score += (Math.random() - 0.5) * 30;

    scored.push({{recipe, score, matched, missing, matchedCore}});
  }}

  scored.sort((a, b) => b.score - a.score);

  if (scored.length === 0) {{
    document.getElementById('recommend-results').innerHTML = '<div style="text-align:center;padding:2rem;color:var(--text-light)"><p style="font-size:1.1rem">😕 没有找到匹配的菜谱</p><p style="margin-top:.5rem">试试选择更多食材，或使用「AI 动态生成」功能</p></div>';
    return;
  }}

  // 从 top N*2 候选池随机抽样 5 道
  const poolSize = Math.min(scored.length, Math.max(5 * 2, 5 + 2));
  const pool = scored.slice(0, poolSize);
  // 随机抽样
  const picked = [];
  while (picked.length < Math.min(5, pool.length) && pool.length > 0) {{
    const idx = Math.floor(Math.random() * pool.length);
    picked.push(pool.splice(idx, 1)[0]);
  }}

  renderResults(picked, ings, 'recommend-results');
}}

function renderResults(items, userIngs, containerId) {{
  const container = document.getElementById(containerId);
  if (items.length === 0) {{
    container.innerHTML = '<p style="text-align:center;color:var(--text-light)">暂无结果</p>';
    return;
  }}

  container.innerHTML = '<div class="recipe-results">' + items.map(item => {{
    const r = item.recipe;
    const matched = item.matched || [];
    const missing = item.missing || [];
    const isAI = r.ai_generated;
    const imgUrl = `${{BACKEND_URL}}/api/v1/recipes/${{r.id}}/image`;
    const reason = isAI
      ? `AI 根据你现有的 ${{matched.slice(0,3).join('、') || userIngs.slice(0,3).join('、')}} 创意推荐`
      : generateReason(r.name, matched, missing);

    return `<div class="recipe-card" onclick="showDetail('${{r.id}}')">
      <img src="${{imgUrl}}" onerror="this.style.display='none';this.parentElement.innerHTML='<div style=\\'height:180px;display:flex;align-items:center;justify-content:center;font-size:3rem;background:var(--gray)\\'>🍳</div>'" loading="lazy">
      <div class="info">
        ${{isAI ? '<span class="ai-tag">✨ AI 生成</span>' : ''}}
        <div class="name">${{r.name}}</div>
        <div class="desc">${{r.description || ''}}</div>
        <div style="margin:.4rem 0">
          ${{matched.length > 0 ? `<span class="matched">✓ 已有: ${{matched.slice(0,4).join('、')}}${{matched.length>4?'...':''}}</span><br>` : ''}}
          ${{missing.length > 0 ? `<span class="missing">还需: ${{missing.slice(0,3).join('、')}}${{missing.length>3?'...':''}}</span>` : '<span class="matched">✓ 食材齐全！</span>'}}
        </div>
        <div class="meta">
          <span>⏱ ${{r.cooking_time || '?'}}</span>
          <span>🍽 ${{r.servings || '?'}}</span>
          <span>📊 ${{r.difficulty || '?'}}</span>
        </div>
        <div class="reason">${{reason}}</div>
      </div>
    </div>`;
  }}).join('') + '</div>';
}}

function generateReason(name, matched, missing) {{
  const templates = [
    `你选了${{matched.slice(0,2).join('和')}}，做${{name}}正合适，简单又好吃`,
    `${{name}}用到了你现有的${{matched.slice(0,2).join('、')}}，家常味道不会出错`,
    `现有食材就能做的${{name}}，${{missing.length === 0 ? '所有食材都齐了' : '只需再补' + missing.slice(0,2).join('、')}}`,
    `${{matched.slice(0,1)[0]}}是主角的${{name}}，搭配你现有的食材，营养又美味`,
  ];
  return templates[Math.floor(Math.random() * templates.length)];
}}

// AI 生成模拟
async function aiGenerate() {{
  if (selectedNovel.size === 0) {{
    document.getElementById('ai-results').innerHTML = '<p style="text-align:center;color:var(--text-light);padding:2rem">请先选择上方食材 ✨</p>';
    return;
  }}

  const ings = Array.from(selectedNovel);
  const container = document.getElementById('ai-results');
  container.innerHTML = `<div class="loading"><div class="spinner"></div><p style="margin-top:1rem">AI 正在根据 ${{ings.join('、')}} 生成创意菜谱...</p></div>`;

  // 尝试调用后端 API
  try {{
    const resp = await fetch(`${{BACKEND_URL}}/api/v1/recipes/recommend`, {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{ingredients: ings, preferences: {{}}, mode: 'normal'}})
    }});
    if (resp.ok) {{
      const data = await resp.json();
      const aiRecipes = data.recipes.map(r => ({{
        recipe: {{
          ...r,
          id: r.id,
          ingredients: r.ingredients,
          ai_generated: r.recommendation_reason && r.recommendation_reason.includes('AI')
        }},
        matched: r.matched_ingredients || [],
        missing: r.missing_ingredients || []
      }}));
      renderResults(aiRecipes, ings, 'ai-results');
      return;
    }}
  }} catch(e) {{
    // 后端不可用，使用模拟数据
  }}

  // 模拟 AI 生成
  setTimeout(() => {{
    const mockAI = generateMockAI(ings);
    renderResults(mockAI, ings, 'ai-results');
  }}, 1500);
}}

function generateMockAI(ings) {{
  const templates = [
    {{name: `${{ings[0]}}创意沙拉`, desc: `清爽健康的创意沙拉，保留食材原味`, steps: ['将食材洗净切好', '调制油醋汁', '拌匀即可'], time: '10分钟', taste: '清爽', diff: '简单'}},
    {{name: `${{ings[0]}}炒蛋`, desc: `简单快手的家常炒蛋，营养美味`, steps: ['鸡蛋打散', '热锅下油炒蛋', '加入食材翻炒调味'], time: '15分钟', taste: '咸鲜', diff: '简单'}},
    {{name: `奶油${{ings[0]}}意面`, desc: `西式创意做法，浓郁顺滑`, steps: ['煮意面', '制作奶油酱', '加入食材拌匀'], time: '25分钟', taste: '奶香', diff: '中等'}},
  ];
  return templates.slice(0, 3).map(t => ({{
    recipe: {{
      id: 'mock-' + Math.random().toString(36).substr(2,9),
      name: t.name,
      description: t.desc,
      ingredients: [...ings, '盐', '橄榄油'],
      cooking_time: t.time,
      servings: '2人份',
      taste: t.taste,
      difficulty: t.diff,
      category: 'AI创意',
      ai_generated: true,
      steps: t.steps
    }},
    matched: ings,
    missing: []
  }}));
}}

// 菜谱详情
function showDetail(id) {{
  const r = RECIPES.find(x => x.id === id);
  if (!r) return;
  const imgUrl = `${{BACKEND_URL}}/api/v1/recipes/${{r.id}}/image`;

  document.getElementById('modal-title').textContent = r.name;
  const ings = (r.ingredients || []);
  const userIngs = Array.from(selectedIngredients);
  document.getElementById('modal-body').innerHTML = `
    <img src="${{imgUrl}}" onerror="this.style.display='none'" loading="lazy">
    <p style="color:var(--text-light);margin-bottom:1rem">${{r.description || ''}}</p>
    <div class="section-label">📋 所需食材</div>
    <div class="ingredients-list">${{ings.map(i => {{
      const have = userIngs.some(u => normalizeIng(u) === normalizeIng(i));
      return `<span class="ing-tag ${{have ? 'have' : 'miss'}}">${{have ? '✓' : '○'}} ${{i}}</span>`;
    }}).join('')}}</div>
    <div class="section-label">👨‍🍳 烹饪步骤</div>
    <div class="steps">${{(r.steps||['步骤1','步骤2']).map(s => `<div class="step"><span>${{s}}</span></div>`).join('')}}</div>
    <div style="display:flex;gap:.8rem;margin-top:1rem;flex-wrap:wrap">
      <span style="background:var(--gray);padding:.4rem 1rem;border-radius:10px;font-size:.85rem">⏱ ${{r.cooking_time||'?'}}</span>
      <span style="background:var(--gray);padding:.4rem 1rem;border-radius:10px;font-size:.85rem">🍽 ${{r.servings||'?'}}</span>
      <span style="background:var(--gray);padding:.4rem 1rem;border-radius:10px;font-size:.85rem">👅 ${{r.taste||'?'}}</span>
      <span style="background:var(--gray);padding:.4rem 1rem;border-radius:10px;font-size:.85rem">📊 ${{r.difficulty||'?'}}</span>
    </div>
  `;
  document.getElementById('modal').classList.add('show');
}}

function closeModal() {{
  document.getElementById('modal').classList.remove('show');
}}

// Gallery
function initGallery() {{
  const categories = ['全部', ...new Set(RECIPES.map(r => r.category || '其他'))];
  const filterContainer = document.getElementById('gallery-filters');
  filterContainer.innerHTML = categories.map(c =>
    `<span class="gallery-filter ${{c === '全部' ? 'active' : ''}}" onclick="filterGallery('${{c}}', this)">${{c}}</span>`
  ).join('');
  renderGallery('全部');
}}

function filterGallery(cat, el) {{
  document.querySelectorAll('.gallery-filter').forEach(f => f.classList.remove('active'));
  el.classList.add('active');
  renderGallery(cat);
}}

function renderGallery(cat) {{
  const grid = document.getElementById('gallery-grid');
  const filtered = cat === '全部' ? RECIPES : RECIPES.filter(r => (r.category || '其他') === cat);
  grid.innerHTML = filtered.map(r => {{
    const imgUrl = `${{BACKEND_URL}}/api/v1/recipes/${{r.id}}/image`;
    return `<div class="gallery-item" onclick="showDetail('${{r.id}}')">
      <img src="${{imgUrl}}" onerror="this.parentElement.innerHTML='<div class=\\'g-emoji\\' style=\\'height:140px\\'>'+'🍳'+'</div><div class=\\'g-name\\'>'+'${{r.name}}'+'</div>'" loading="lazy">
      <div class="g-name">${{r.name}}</div>
    </div>`;
  }}).join('');
}}

// Tab 切换
function switchTab(tab) {{
  document.querySelectorAll('.demo-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.demo-panel').forEach(p => p.classList.remove('active'));
  event.currentTarget.classList.add('active');
  document.getElementById('panel-' + tab).classList.add('active');
}}

// 初始化
initIngredients();
initGallery();
</script>
</body>
</html>"""


def main():
    print("正在获取菜谱数据...")
    recipes = fetch_recipes()
    print(f"获取到 {len(recipes)} 道菜谱")

    html = build_html(recipes)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode("utf-8")) / 1024
    print(f"已生成: {OUTPUT} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
