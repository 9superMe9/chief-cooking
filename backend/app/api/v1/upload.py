"""
图片上传与食材识别接口。
存储后端根据配置自动切换：
- COS_BUCKET 已配置 -> 上传到腾讯云 COS，返回公网 URL
- 否则 -> 存本地 ./uploads，URL 由 PUBLIC_BASE_URL 拼接（小程序需公网 HTTPS 地址）
"""
import os
import uuid
import base64
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.core.config import settings
from app.services.ai import AIService

router = APIRouter()

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTS = (".png", ".jpg", ".jpeg")
MAX_SIZE = 5 * 1024 * 1024


def _is_cos_configured() -> bool:
    return bool(
        settings.COS_SECRET_ID
        and settings.COS_SECRET_KEY
        and settings.COS_BUCKET
        and not settings.COS_SECRET_ID.startswith("your-")
    )


def _local_public_url(file_name: str) -> str:
    """拼接本地图片的访问 URL；PUBLIC_BASE_URL 配置后为公网绝对地址"""
    base = settings.PUBLIC_BASE_URL.rstrip("/") if settings.PUBLIC_BASE_URL else ""
    if base:
        return f"{base}/uploads/{file_name}"
    return f"/uploads/{file_name}"


def _upload_to_cos(content: bytes, file_name: str) -> str:
    """上传到腾讯云 COS，返回公网访问 URL。COS SDK 按需导入。"""
    from qcloud_cos import CosConfig, CosS3Client  # type: ignore

    config = CosConfig(
        Region=settings.COS_REGION,
        SecretId=settings.COS_SECRET_ID,
        SecretKey=settings.COS_SECRET_KEY,
        Scheme="https",
    )
    client = CosS3Client(config)
    key = f"ingredients/{file_name}"
    client.put_object(Bucket=settings.COS_BUCKET, Body=content, Key=key)
    return f"https://{settings.COS_BUCKET}.cos.{settings.COS_REGION}.myqcloud.com/{key}"


@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(ALLOWED_EXTS):
        raise HTTPException(status_code=400, detail="只支持png/jpg/jpeg格式")

    content = await file.read()
    file_size = len(content)

    if file_size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="图片大小不能超过5MB")

    file_ext = file.filename.split(".")[-1]
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}.{file_ext}"

    if _is_cos_configured():
        try:
            image_url = _upload_to_cos(content, file_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"图片上传失败: {e}")
        storage = "cos"
    else:
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(content)
        image_url = _local_public_url(file_name)
        storage = "local"

    return {
        "file_id": file_id,
        "file_name": file_name,
        "image_url": image_url,
        "size": file_size,
        "storage": storage,
    }


@router.post("/ingredients/recognize")
async def recognize_ingredients(file_id: str = None, image_url: str = None):
    # 优先用公网 URL（COS 或 PUBLIC_BASE_URL 拼接的绝对地址），否则读本地文件转 base64
    image_data_url = None
    local_path = None

    if image_url and image_url.startswith(("http://", "https://")):
        # 公网地址：百炼多模态可直接访问；但为稳定仍可选本地回退
        image_data_url = image_url
    elif image_url and image_url.startswith("/uploads/"):
        local_path = os.path.join(".", image_url.lstrip("/"))
    elif file_id:
        for ext in ("png", "jpg", "jpeg"):
            candidate = os.path.join(UPLOAD_DIR, f"{file_id}.{ext}")
            if os.path.exists(candidate):
                local_path = candidate
                break

    # 本地文件转 base64 data url
    if not image_data_url and local_path and os.path.exists(local_path):
        ext = local_path.rsplit(".", 1)[-1].lower()
        mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, "image/jpeg")
        with open(local_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        image_data_url = f"data:{mime};base64,{b64}"

    if not image_data_url:
        raise HTTPException(status_code=404, detail="图片不存在，请先上传")

    # 调用 AI 识别，失败时返回空列表由前端降级到手动输入
    ingredients = await AIService.recognize_ingredients(image_data_url)

    if not ingredients:
        return {
            "file_id": file_id,
            "image_url": image_url,
            "ingredients": [],
            "ai_available": False,
            "message": "AI识别不可用，请手动输入食材",
        }

    return {
        "file_id": file_id,
        "image_url": image_url,
        "ingredients": [
            {"id": str(uuid.uuid4()), **ing, "status": "pending"}
            for ing in ingredients
        ],
        "ai_available": True,
        "message": "AI识别结果，请确认识别内容",
    }
