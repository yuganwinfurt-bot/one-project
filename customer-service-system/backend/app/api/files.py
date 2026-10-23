import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.common.exceptions import BusinessException
from app.common.response import Response
from app.config import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_DIR
from app.dependencies.auth import CurrentUser
from app.schemas.file import FileResponse

router = APIRouter(prefix="/files", tags=["文件管理"])


@router.post("/upload")
def upload(
    _user: CurrentUser,
    file: Annotated[UploadFile, File()],
):
    """文件上传的接口"""
    if not file.filename:
        raise BusinessException(message="文件名不能为空")

    # 原始的文件名  用户头像.jpg
    orignal_name = os.path.basename(file.filename)
    # 文件后缀 .jpg
    ext = Path(orignal_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise BusinessException(message=f"不自持的文件后缀：{ext}")
    # 文件大小校验：file.size 正常由框架填充，为空时也不能放过
    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise BusinessException(
            message=f"文件不能超过 {MAX_FILE_SIZE // 1024 // 1024}MB"
        )
    # 设置唯一的文件名称   199323213213_ddadaqwerq.jpg
    disk_name = f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}{ext}"
    # 文件存储的实际路径
    save_path = UPLOAD_DIR / disk_name

    # 流式写文件
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 兜底：以实际落盘字节数再校验一次，超出上限就删除并拒绝
    written = save_path.stat().st_size
    if written > MAX_FILE_SIZE:
        save_path.unlink(missing_ok=True)
        raise BusinessException(
            message=f"文件不能超过 {MAX_FILE_SIZE // 1024 // 1024}MB"
        )

    return Response.success(
        data=FileResponse(
            original_name=orignal_name,
            disk_name=disk_name,
            size=written,
            url=f"/uploads/{disk_name}",
        )
    )
