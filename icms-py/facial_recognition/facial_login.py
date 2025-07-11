import asyncio
import logging
import cv2
from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from deepface import DeepFace
from core.state import app_state
from .facial import MODEL_NAME, VIDEO_STREAM_URL, DETECTOR_BACKEND

# 配置和路由
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai/facial/login", tags=["Facial Login"])


# Pydantic 模型定义:定义从 Spring Boot 发来的请求体
class CompareRequest(BaseModel):
    username: str
    faceEmbedding: str


async def capture_and_process_frame():
    """
    捕获一帧视频并进行人脸识别处理
    """
    # 1. 打开视频流
    cap = cv2.VideoCapture(VIDEO_STREAM_URL)
    if not cap.isOpened():
        logger.error(f"无法打开视频流: {VIDEO_STREAM_URL}")
        raise HTTPException(status_code=500, detail="无法连接到视频流")

    try:
        # 2. 读取一帧
        ret, frame = cap.read()
        if not ret:
            raise HTTPException(status_code=500, detail="无法从视频流读取帧")

        # 3. 使用 DeepFace 进行人脸识别
        results = await asyncio.to_thread(
            DeepFace.represent,
            img_path=frame,
            model_name=MODEL_NAME,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True
        )

        if not results or len(results) == 0:
            raise HTTPException(status_code=400, detail="未检测到人脸，请正对摄像头")

        # 4. 获取人脸特征向量
        face_info = results[0]
        vector = face_info['embedding']
        return vector

    except ValueError as ve:
        raise HTTPException(status_code=400, detail="未检测到人脸，请正对摄像头")
    except Exception as e:
        logger.error(f"处理视频帧时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"处理视频帧时发生错误: {str(e)}")
    finally:
        cap.release()


# 人脸登录接口
@router.post("/compare")
async def compare_face(request: CompareRequest):
    """
    接收来自后端服务的用户已存储向量，
    并与当前摄像头捕捉到的实时向量进行比对。
    """
    logger.info(f"收到用户 '{request.username}' 的人脸比对任务。")

    try:
        # 1. 捕获实时视频帧并生成向量
        realtime_vector = await capture_and_process_frame()

        # 2. 处理存储的向量
        try:
            stored_vector_list = [float(x) for x in request.faceEmbedding.split(',')]
        except (ValueError, AttributeError):
            logger.error(f"接收到来自后端的格式错误的向量字符串: {request.faceEmbedding}")
            raise HTTPException(status_code=400, detail="提供的向量字符串格式不正确。")

        logger.info(f"开始比对用户 '{request.username}' 的实时向量与数据库向量。")

        # 3. 使用 DeepFace.verify 进行比对
        verification_result = await asyncio.to_thread(
            DeepFace.verify,
            img1_representation=realtime_vector,
            img2_representation=stored_vector_list,
            model_name=MODEL_NAME,
            detector_backend='skip'
        )

        is_verified = verification_result.get("verified", False)
        logger.info(f"用户 '{request.username}' 比对完成。结果是否匹配: {is_verified}")

        # 4. 将详细的比对结果返回给 Spring Boot
        return {
            "status": "success",
            "verified": is_verified,
            "distance": verification_result.get("distance"),
            "threshold": verification_result.get("threshold"),
            "message": "比对操作成功完成。"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"人脸比对过程中发生严重错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"人脸比对服务内部发生错误: {str(e)}"
        )