# 🍳 饭点小厨

> AI 驱动的智能菜谱推荐助手 —— 让每一餐都有灵感

<p>
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/uni--app-3.0-2196F3?logo=data:image/svg+xml;base64,&logoColor=white" alt="uni-app">
  <img src="https://img.shields.io/badge/Vue-3.4-42b883?logo=vuedotjs&logoColor=white" alt="Vue">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/AI-Qwen3.7--Plus-615CED" alt="Qwen">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

## 📖 项目简介

**饭点小厨** 是一款基于 AI 的智能菜谱推荐应用。用户通过拍照识别冰箱食材，AI 根据现有食材智能推荐菜谱；当菜谱库匹配不足时，AI 会动态生成全新菜谱。项目采用前后端分离架构，支持 H5 和微信小程序多端部署。

### 🎯 核心功能

| 功能 | 说明 | 技术实现 |
|------|------|----------|
| 📸 **AI 拍照识食材** | 拍照上传冰箱食材，AI 多模态模型自动识别 | Qwen3.7-Plus 多模态视觉理解 |
| 🧠 **智能菜谱推荐** | 根据现有食材匹配菜谱，支持"几菜几汤"自定义 | 核心食材覆盖率评分 + ±15 随机扰动 + Top N×2 候选池抽样 |
| ✨ **AI 动态菜谱生成** | 菜谱库匹配不足时，AI 实时生成全新菜谱 | Qwen3.7-Plus 文本生成 + 10min 缓存 + 1h 自动清理 |
| 📊 **Token 用量追踪** | 实时监控 AI 调用成本，80% 额度自动预警 | 本地 JSON 记录 + 日志告警 |
| 🔒 **接口限流** | 防止滥用，按路由组分别限速 | 自定义中间件（登录/AI 10次/分钟） |

### ✨ 项目亮点

- **混合推荐策略**：固定菜谱库 58 道 + AI 动态生成无限覆盖，既保证质量又覆盖长尾需求
- **推荐多样性**：±15 随机扰动 + 候选池随机抽样，每次"重新推荐"都有不同组合
- **成本可控**：10 分钟相同食材组合不重复调用 AI，1 小时后自动清理临时菜谱
- **真实食物照片**：58 道菜谱均使用 Pollinations.ai Flux 模型生成 512×512 真实食物照片
- **多端适配**：uni-app 一套代码，同时支持 H5、微信小程序、支付宝小程序等

## 🏗️ 技术架构

```
┌──────────┐     ┌──────────────┐     ┌──────────────────┐
│  用户端   │────▶│  前端 (H5)   │────▶│  后端 (FastAPI)  │
│ 手机/PC  │     │  uni-app     │     │  异步 API        │
└──────────┘     └──────────────┘     └────────┬─────────┘
                                                │
                         ┌──────────────────────┼──────────────────────┐
                         ▼                      ▼                      ▼
                 ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
                 │  阿里云百炼   │      │  Pollinations │      │  数据库       │
                 │  Qwen3.7-Plus│      │  Flux 图片    │      │  SQLite/PG   │
                 │  多模态 AI   │      │  生成服务     │      │  SQLAlchemy  │
                 └──────────────┘      └──────────────┘      └──────────────┘
```

## 🛠️ 技术栈

### 后端
- **FastAPI** 0.104 — 异步 Web 框架
- **SQLAlchemy** 2.0 — 异步 ORM
- **Alembic** — 数据库迁移
- **python-jose** — JWT 认证
- **Loguru** — 日志管理
- **SQLite / PostgreSQL** — 数据库（开发/生产）

### 前端
- **uni-app** 3.0 — 跨端框架（H5 + 小程序）
- **Vue** 3.4 — 前端框架
- **Pinia** — 状态管理
- **TypeScript** — 类型安全
- **Vite** 5.2 — 构建工具

### AI & 第三方服务
- **阿里云百炼 Qwen3.7-Plus** — 多模态 AI（食材识别 + 菜谱生成 + 推荐润色）
- **Pollinations.ai Flux** — 菜谱图片生成
- **腾讯云 COS** — 图片存储（可选）
- **Cloudflare Tunnel** — 公网访问

## 📁 项目结构

```
chief-cooking/
├── backend/                     # 后端服务
│   ├── app/
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── api/v1/              # REST API 路由
│   │   │   ├── auth.py          #   用户认证（注册/登录）
│   │   │   ├── recipes.py       #   菜谱推荐与浏览
│   │   │   ├── ingredients.py   #   食材识别与管理
│   │   │   ├── favorites.py     #   菜谱收藏
│   │   │   ├── upload.py        #   图片上传
│   │   │   └── health.py        #   健康检查
│   │   ├── core/                # 核心配置
│   │   │   ├── config.py        #   环境变量配置
│   │   │   ├── security.py      #   JWT 安全
│   │   │   └── logging.py       #   日志配置
│   │   ├── db/                  # 数据库
│   │   │   ├── session.py       #   异步会话
│   │   │   └── migrations/      #   Alembic 迁移
│   │   ├── models/              # ORM 模型
│   │   │   ├── user.py          #   用户
│   │   │   ├── recipe.py        #   菜谱
│   │   │   ├── ingredient.py    #   食材会话
│   │   │   └── favorite.py      #   收藏
│   │   ├── schemas/             # Pydantic 数据模型
│   │   ├── services/            # 业务逻辑层
│   │   │   ├── ai.py            #   AI 服务（识别/生成/润色）
│   │   │   ├── recipe.py        #   推荐算法
│   │   │   ├── ingredient.py    #   食材管理
│   │   │   └── image.py         #   图片服务
│   │   ├── middleware/          # 中间件
│   │   │   └── rate_limit.py    #   接口限流
│   │   └── utils/               # 工具
│   │       ├── token_usage.py   #   Token 用量追踪
│   │       └── sensitive_words.py #  敏感词过滤
│   ├── static/recipes/          # 58 道菜谱真实照片
│   ├── requirements.txt
│   └── .env.example             # 环境变量模板
├── frontend/                    # 前端应用
│   ├── src/
│   │   ├── pages/               # 页面（12个）
│   │   │   ├── index/           #   首页
│   │   │   ├── confirm/         #   食材确认
│   │   │   ├── preference/      #   偏好设置
│   │   │   ├── result/          #   推荐结果
│   │   │   ├── detail/          #   菜谱详情
│   │   │   ├── recipe-browse/   #   菜谱浏览
│   │   │   ├── favorites/       #   收藏
│   │   │   ├── history/         #   历史
│   │   │   └── profile/         #   个人中心
│   │   ├── api/                 # API 请求封装
│   │   ├── components/          # 公共组件
│   │   ├── stores/              # Pinia 状态管理
│   │   └── utils/               # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── deploy/
│   └── nginx.conf               # Nginx 部署配置
├── demo.html                    # 交互式演示页面
└── .gitignore
```

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- 阿里云百炼 API Key（[获取地址](https://dashscope.aliyuncs.com)）

### 1. 克隆项目

```bash
git clone https://github.com/9superMe9/chief-cooking.git
cd chief-cooking
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 AI_API_KEY 等配置

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端启动后：
- API 服务：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`（仅开发环境）

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 配置后端地址
# 编辑 .env，设置 VITE_API_BASE_URL=http://localhost:8000/api/v1

# H5 开发模式
npm run dev:h5

# 构建生产版本
npm run build:h5
```

前端启动后访问：`http://localhost:5173`

### 4. 交互式 Demo

项目根目录包含 `demo.html`，是一个自包含的交互式演示页面，无需启动前端即可体验核心功能：

```bash
# 确保 backend/static/demo.html 存在，后端启动后直接访问
# 本地访问
http://localhost:8000/demo.html

# 或通过 Cloudflare Tunnel 公网访问
cloudflared tunnel --url http://localhost:8000
# 获得公网 URL 后访问 https://<your-tunnel>.trycloudflare.com/demo.html
```

## ⚙️ 配置说明

### 后端环境变量（`.env`）

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `APP_ENV` | 运行环境（development/production） | development |
| `DATABASE_URL` | 数据库连接 | sqlite+aiosqlite:///./chief_cooking.db |
| `AI_API_KEY` | 阿里云百炼 API Key | （必填） |
| `AI_VISION_MODEL` | 视觉模型 | qwen3.7-plus |
| `AI_TEXT_MODEL` | 文本模型 | qwen3.7-plus |
| `AI_FREE_QUOTA_TOKENS` | 免费额度（tokens） | 1000000 |
| `JWT_SECRET_KEY` | JWT 密钥 | （必填，请生成强密钥） |
| `CORS_ORIGINS` | CORS 允许来源 | http://localhost:5173 |
| `RATE_LIMIT_AI_PER_MIN` | AI 接口限流 | 10 |

完整配置见 [backend/.env.example](backend/.env.example)

### 前端环境变量

```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/health` | 健康检查 |
| `POST` | `/api/v1/auth/register` | 用户注册 |
| `POST` | `/api/v1/auth/login` | 用户登录 |
| `POST` | `/api/v1/ingredients/sessions` | 创建食材会话（拍照识别） |
| `GET` | `/api/v1/ingredients/sessions/{id}` | 获取食材会话 |
| `POST` | `/api/v1/recipes/recommend` | 智能菜谱推荐 |
| `GET` | `/api/v1/recipes` | 浏览全部菜谱 |
| `GET` | `/api/v1/recipes/{id}` | 菜谱详情 |
| `GET` | `/api/v1/recipes/{id}/image` | 菜谱封面图 |
| `POST` | `/api/v1/favorites` | 添加收藏 |
| `GET` | `/api/v1/favorites` | 收藏列表 |
| `GET` | `/api/v1/recommendations/history` | 推荐历史 |

启动后端后访问 `http://localhost:8000/docs` 查看完整 Swagger 文档。

## 🧠 推荐算法

推荐系统采用**核心食材覆盖率评分** + **随机扰动** + **候选池抽样**的三层策略：

```
评分 = 核心食材覆盖率 × 70 + 总食材覆盖率 × 30 + 随机扰动(±15)
```

1. **核心食材覆盖率**：主料（如鸡蛋、猪肉）匹配权重 70%，辅料（如葱、盐）不计入缺失
2. **随机扰动**：±15 分随机扰动，让每次推荐结果有变化
3. **候选池抽样**：从 Top N×2 候选池中随机抽样 N 道，增加推荐多样性

**混合推荐流程**：
```
用户食材 → 固定菜谱库匹配 → 匹配 ≥ 3 道？ 
  ├─ 是 → 返回推荐结果
  └─ 否 → 调用 AI 动态生成补充 → 返回混合结果
```

## 📦 部署

### Docker + Nginx 部署

```bash
# 构建前端
cd frontend && npm run build:h5

# 将前端构建产物复制到后端 static 目录
cp -r dist/* ../backend/static/

# 启动后端
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Nginx 反向代理配置参考 [deploy/nginx.conf](deploy/nginx.conf)。

### 生产环境注意事项

- 数据库切换为 PostgreSQL：`DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname`
- 设置 `APP_ENV=production` 关闭 API 文档
- 生成强 JWT 密钥：`python -c "import secrets; print(secrets.token_urlsafe(48))"`
- 配置 CORS 白名单为实际域名
- 启用腾讯云 COS 替代本地图片存储

## 📝 开发约定

- API Key 等敏感信息通过 `.env` 管理，已加入 `.gitignore`
- 数据库迁移使用 Alembic（`backend/app/db/migrations/`）
- AI 生成菜谱以 `ai_reason="__AI_GENERATED__"` 标记，1 小时后自动清理
- 菜谱图片使用 Pollinations.ai Flux 模型生成（512×512）
- 接口限流：登录/AI 接口 10 次/分钟，上传 20 次/分钟

## 📄 License

MIT License

## 🙏 致谢

- [阿里云百炼](https://dashscope.aliyuncs.com) — AI 多模态模型服务
- [Pollinations.ai](https://pollinations.ai) — AI 图片生成
- [FastAPI](https://fastapi.tiangolo.com) — 后端框架
- [uni-app](https://uniapp.dcloud.io) — 跨端前端框架

---

<p align="center">Made with ❤️ for Trae AI Competition</p>
