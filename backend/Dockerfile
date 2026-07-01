# 饭点小厨后端镜像：Python 3.12 + FastAPI
FROM python:3.12-slim

WORKDIR /app

# 系统依赖（Pillow/bcrypt 等需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 上传目录（本地存储时使用；COS 模式下不用）
RUN mkdir -p /app/uploads /app/logs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
