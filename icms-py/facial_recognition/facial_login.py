import asyncio
import logging
import numpy as np
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from deepface import DeepFace
from .facial import facial_service, MODEL_NAME
from .utils import FaceEncoder, AdvancedLivenessChecker
# 配置和路由
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai/facial/login", tags=["Facial Login"])

class CompareRequest(BaseModel):
    username: str
    faceEmbedding: str

class SigninRequest(BaseModel):
    username: str
    faceImage: str
    faceEmbedding: str


def calculate_cosine_similarity(vector1, vector2):
    """计算余弦相似度"""
    # 转换为numpy数组
    v1 = np.array(vector1)
    v2 = np.array(vector2)

    # 计算余弦相似度
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    similarity = dot_product / (norm_v1 * norm_v2)
    return similarity


def calculate_euclidean_distance(vector1, vector2):
    """计算欧氏距离"""
    v1 = np.array(vector1)
    v2 = np.array(vector2)
    return np.linalg.norm(v1 - v2)


@router.post("/compare")
async def compare_face(request: CompareRequest):
    """
    接收来自后端的用户向量，与摄像头实时捕捉到的人脸进行比对和活体检测
    """
    logger.info(f"收到用户 '{request.username}' 的人脸比对任务。")

    # 从 facial_service 获取最新的实时人脸数据
    realtime_result = await facial_service.get_latest_face_info()

    # 是否检测到人脸或者保持不变
    if not realtime_result or "vector_list" not in realtime_result:
        logger.warning(f"比对失败：用户'{request.username}'未正对摄像头或未检测到人脸。")
        raise HTTPException(
            status_code=400,
            detail="摄像头当前未检测到人脸，请正对摄像头后重试。"
        )

    liveness_passed = realtime_result.get("liveness_passed", False)
    if not liveness_passed:
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

        if len(stored_vector_list) != len(realtime_vector_list):
            logger.error(f"向量维度不匹配: 存储向量{len(stored_vector_list)}, 实时向量{len(realtime_vector_list)}")
            raise HTTPException(status_code=400, detail="向量维度不匹配")

    except (ValueError, AttributeError, KeyError) as e:
        logger.error(f"接收到格式错误的向量或实时数据不完整: {e}")
        raise HTTPException(status_code=400, detail="提供的向量字符串格式不正确或实时数据异常。")

    # 核心比对逻辑
    try:
        logger.info(f"开始比对用户 '{request.username}' 的实时向量与数据库向量。")

        # 方法1：使用余弦相似度（推荐）
        similarity = calculate_cosine_similarity(realtime_vector_list, stored_vector_list)

        # 方法2：使用欧氏距离作为辅助验证
        distance = calculate_euclidean_distance(realtime_vector_list, stored_vector_list)

        # 设置阈值（根据实际情况调整）
        # 对于Facenet512，通常：
        # - 余弦相似度：> 0.4 为匹配
        # - 欧氏距离：< 10 为匹配
        cosine_threshold = 0.4
        distance_threshold = 15.0

        # 综合判断
        is_verified = bool(similarity > cosine_threshold and distance < distance_threshold)  # 转换为Python原生布尔值

        logger.info(
            f"用户 '{request.username}' 比对完成。余弦相似度: {similarity:.4f}, 欧氏距离: {distance:.4f}, 匹配: {is_verified}")

        return {
            "status": "success",
            "verified": is_verified,  # 现在是Python原生布尔值
            "cosine_similarity": float(similarity),  # 确保是Python float
            "euclidean_distance": float(distance),  # 确保是Python float
            "cosine_threshold": float(cosine_threshold),  # 确保是Python float
            "distance_threshold": float(distance_threshold),  # 确保是Python float
            "message": "比对操作成功完成。"
        }

    except Exception as e:
        logger.error(f"人脸比对过程中发生严重错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"人脸比对服务内部发生错误: {e}"
        )


@router.post("/compare_deepface")
async def compare_face_deepface(request: CompareRequest):
    """
    使用DeepFace.verify的备用比对方法（较慢但更准确）
    """
    logger.info(f"收到用户 '{request.username}' 的DeepFace比对任务。")

    # 从 facial_service 获取最新的实时人脸数据
    realtime_result = await facial_service.get_latest_face_info()

    # 检查是否检测到人脸
    if not realtime_result or "vector_list" not in realtime_result:
        logger.warning(f"比对失败：用户'{request.username}'未正对摄像头或未检测到人脸。")
        raise HTTPException(
            status_code=400,
            detail="摄像头当前未检测到人脸，请正对摄像头后重试。"
        )

    # 检查活体检测
    liveness_passed = realtime_result.get("liveness_passed", False)
    if not liveness_passed:
        logger.warning(f"比对失败：用户'{request.username}'未通过活体检测。")
        raise HTTPException(
            status_code=403,
            detail="活体检测失败，请确保是您本人且光线良好，请勿使用照片或视频。"
        )

    # 准备比对向量
    try:
        # 从请求中获取存储的向量
        stored_vector_list = [float(x) for x in request.faceEmbedding.split(',')]
        # 从实时结果中获取向量
        realtime_vector_list = realtime_result['vector_list']

    except (ValueError, AttributeError, KeyError) as e:
        logger.error(f"接收到格式错误的向量或实时数据不完整: {e}")
        raise HTTPException(status_code=400, detail="提供的向量字符串格式不正确或实时数据异常。")

    # 使用DeepFace.verify进行比对
    try:
        logger.info(f"开始DeepFace比对用户 '{request.username}' 的实时向量与数据库向量。")

        # 使用 asyncio.to_thread 运行阻塞的 verify 函数
        verification_result = await asyncio.to_thread(
            DeepFace.verify,
            img1_representation=realtime_vector_list,
            img2_representation=stored_vector_list,
            model_name=MODEL_NAME,
            detector_backend='skip'  # 因为我们已经有向量了，所以跳过检测
        )

        is_verified = bool(verification_result.get("verified", False))  # 转换为Python原生布尔值
        logger.info(f"用户 '{request.username}' DeepFace比对完成。结果是否匹配: {is_verified}")

        return {
            "status": "success",
            "verified": is_verified,  # 现在是Python原生布尔值
            "distance": float(verification_result.get("distance", 0)),  # 确保是Python float
            "threshold": float(verification_result.get("threshold", 0)),  # 确保是Python float
            "message": "DeepFace比对操作成功完成。"
        }

    except Exception as e:
        logger.error(f"DeepFace人脸比对过程中发生严重错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"DeepFace人脸比对服务内部发生错误: {e}"
        )

@router.post("/signin")
async def compare_face_signin(request: Request, signin_request: SigninRequest):
    """
    接收来自后端的用户向量，与摄像头实时捕捉到的人脸进行比对和活体检测
    """
    logger.info(f"收到签到请求 - URL: {request.url}")
    logger.info(f"请求方法: {request.method}")
    logger.info(f"请求头: {request.headers}")
    logger.info(f"收到用户 '{signin_request.username}' 的签到任务。")

    # 从图像字符串中提取签到时的人脸向量
    signinFaceResult = FaceEncoder.extract_vector_from_image(signin_request.faceImage)
    if not signinFaceResult:
        logger.warning(f"签到失败：无法从图像中提取人脸向量。")
        raise HTTPException(
            status_code=400,
            detail="无法从图像中提取人脸向量，请确保图像清晰且包含人脸。"
        )

    # 准备比对向量
    try:
        # 从请求中获取存储的向量
        storedFaceEmbedding = [float(x) for x in signin_request.faceEmbedding.split(',')]
        # 从签到图像中获取向量
        signinFaceEmbedding = signinFaceResult['vector_list']

        if len(storedFaceEmbedding) != len(signinFaceEmbedding):
            logger.error(f"向量维度不匹配: 存储向量{len(storedFaceEmbedding)}, 签到向量{len(signinFaceEmbedding)}")
            raise HTTPException(status_code=400, detail="向量维度不匹配")

    except (ValueError, AttributeError, KeyError) as e:
        logger.error(f"处理向量数据时发生错误: {e}")
        raise HTTPException(status_code=400, detail="提供的向量数据格式不正确。")

    # 核心比对逻辑
    try:
        logger.info(f"开始比对用户 '{signin_request.username}' 的签到向量与数据库向量。")

        # 方法1：使用余弦相似度（推荐）
        similarity = calculate_cosine_similarity(signinFaceEmbedding, storedFaceEmbedding)

        # 方法2：使用欧氏距离作为辅助验证
        distance = calculate_euclidean_distance(signinFaceEmbedding, storedFaceEmbedding)

        # 设置阈值（根据实际情况调整）
        cosine_threshold = 0.4
        distance_threshold = 25.0

        # 综合判断
        is_verified = bool(similarity > cosine_threshold and distance < distance_threshold)

        logger.info(
            f"用户 '{signin_request.username}' 比对完成。余弦相似度: {similarity:.4f}, 欧氏距离: {distance:.4f}, 匹配: {is_verified}")

        return {
            "status": "success",
            "verified": is_verified,
            "cosine_similarity": float(similarity),
            "euclidean_distance": float(distance),
            "cosine_threshold": float(cosine_threshold),
            "distance_threshold": float(distance_threshold),
            "message": "比对操作成功完成。"
        }

    except Exception as e:
        logger.error(f"人脸比对过程中发生严重错误: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"人脸比对服务内部发生错误: {str(e)}"
        )