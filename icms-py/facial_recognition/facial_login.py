import asyncio
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from deepface import DeepFace
import numpy as np
from .facial import facial_service, MODEL_NAME

# 配置和路由
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai/facial/login", tags=["Facial Login"])

class CompareRequest(BaseModel):
    username: str
    faceEmbedding: str


@router.post("/compare")
async def compare_face(request: CompareRequest):
    """
    接收来自后端的用户向量，与摄像头实时捕捉到的人脸进行比对和活体检测。
    注意：此接口的请求和响应格式保持不变。
    """
    logger.info(f"收到用户 '{request.username}' 的人脸比对任务。")

    # 从 facial_service 获取最新的实时人脸数据
    realtime_result = await facial_service.get_latest_face_info()

    # 使用新来源的数据进行验证
    if not realtime_result:
        logger.warning(f"比对失败：用户'{request.username}'未正对摄像头或未检测到人脸。")
        raise HTTPException(
            status_code=400,
            detail="摄像头当前未检测到人脸，请正对摄像头后重试。"
        )

    is_live_person = realtime_result.get("is_live", False)
    if not is_live_person:
        logger.warning(f"比对失败：用户'{request.username}'未通过活体检测。")
        raise HTTPException(
            status_code=403,
            detail="活体检测失败，请确保是您本人且光线良好，请勿使用照片或视频。"
        )

    # 准备比对向量
    try:
        # 从请求中获取存储的向量
        stored_vector_list = [float(x) for x in request.faceEmbedding.split(',')]
        # 从实时结果中获取向量 (注意我们现在用 vector_list)
        realtime_vector_list = realtime_result['vector_list']
    except (ValueError, AttributeError, KeyError):
        logger.error(f"接收到格式错误的向量或实时数据不完整: {request.faceEmbedding}")
        raise HTTPException(status_code=400, detail="提供的向量字符串格式不正确或实时数据异常。")

    # 核心比对逻辑
    try:
        logger.info(f"开始比对用户 '{request.username}' 的实时向量与数据库向量。")

        # 使用 asyncio.to_thread 运行阻塞的 verify 函数
        verification_result = await asyncio.to_thread(
            DeepFace.verify,
            img1_representation=realtime_vector_list,
            img2_representation=stored_vector_list,
            model_name=MODEL_NAME,
            detector_backend='skip'  # 因为我们已经有向量了，所以跳过检测
        )

        is_verified = verification_result.get("verified", False)
        logger.info(f"用户 '{request.username}' 比对完成。结果是否匹配: {is_verified}")

        # 返回保持不变
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