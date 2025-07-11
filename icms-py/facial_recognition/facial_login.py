import asyncio
import logging
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from deepface import DeepFace
from core.state import app_state
from .facial import MODEL_NAME

# 配置和路由
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai/facial/login", tags=["Facial Login"])


# Pydantic 模型定义:定义从 Spring Boot 发来的请求体
class CompareRequest(BaseModel):
    username: str
    stored_vector: List[float]


# 人脸登录接口
@router.post("/compare")
async def compare_face(request: CompareRequest):
    """
    接收来自后端服务的用户已存储向量，
    并与当前摄像头捕捉到的实时向量进行比对。
    """
    logger.info(f"收到用户 '{request.username}' 的人脸比对任务。")

    # 1. 从共享状态 app_state 中读取实时人脸向量
    async with app_state.lock:
        realtime_vector = app_state.latest_vector

    if not realtime_vector:
        logger.warning(f"比对失败：用户'{request.username}'未正对摄像头。")
        raise HTTPException(
            status_code=400,
            detail="摄像头当前未检测到人脸，请正对摄像头后重试。"
        )

    # 2. 使用 DeepFace.verify 进行比对
    try:
        logger.info(f"开始比对用户 '{request.username}' 的实时向量与数据库向量。")

        verification_result = await asyncio.to_thread(
            DeepFace.verify,
            img1_representation=realtime_vector,
            img2_representation=request.stored_vector,
            model_name=MODEL_NAME,
            detector_backend='skip'
        )

        is_verified = verification_result.get("verified", False)
        logger.info(f"用户 '{request.username}' 比对完成。结果是否匹配: {is_verified}")

        # 3. 将详细的比对结果返回给 Spring Boot
        return {
            "status": "success",
            "verified": is_verified,
            "distance": verification_result.get("distance"),
            "threshold": verification_result.get("threshold"),
            "message": "比对操作成功完成。"
        }

    except Exception as e:
        logger.error(f"人脸比对过程中发生严重错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"人脸比对服务内部发生错误: {e}"
        )