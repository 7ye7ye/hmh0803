import asyncio
import logging
import cv2
import numpy as np
from deepface import DeepFace

logger = logging.getLogger(__name__)


class FaceEncoder:
    """负责从图像帧中提取人脸特征向量。"""

    def __init__(self, model_name: str, detector_backend: str):
        self.model_name = model_name
        self.detector_backend = detector_backend
        # 预加载模型以提高后续性能
        logger.info(f"正在为 FaceEncoder 预加载模型 '{model_name}'...")
        DeepFace.build_model(model_name)
        logger.info("FaceEncoder 模型预加载完成。")

    async def extract_vector(self, frame: np.ndarray) -> dict | None:
        """
        从单帧图像中提取人脸信息。
        返回: 一个包含向量、区域等信息的字典，如果未检测到则返回 None。
        """
        if frame is None or frame.size == 0:
            return None
        try:
            # 使用 asyncio.to_thread 运行阻塞的 CPU 密集型任务
            results = await asyncio.to_thread(
                DeepFace.represent,
                img_path=frame,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=True  # 强制检测，未检测到会抛出异常
            )
            if not results:
                return None

            # DeepFace.represent 返回一个列表，我们取第一个结果
            face_info = results[0]
            vector = face_info['embedding']

            # 将向量转换为逗号分隔的字符串
            vector_str = ",".join(map(str, vector))

            return {
                "vector_list": vector,
                "vector_str": vector_str,
                "region": face_info['facial_area']
            }
        except ValueError:
            # 这是 DeepFace 在 enforce_detection=True 且未检测到人脸时抛出的常见异常
            logger.info("在帧中未检测到人脸。")
            return None
        except Exception as e:
            logger.warning(f"向量提取过程中发生未知错误: {e}")
            return None


class LivenessChecker:
    """负责对指定的人脸区域进行活体检测。"""

    def __init__(self, prototxt_path: str, model_path: str):
        logger.info("正在加载活体检测模型...")
        self.liveness_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
        logger.info("活体检测模型加载成功。")

    def check(self, frame: np.ndarray, region: dict) -> dict | None:
        """
        在给定的区域进行活体检测。
        返回: 一个包含布尔值和标签的字典，如果失败则返回 None。
        """
        try:
            x, y, w, h = region['x'], region['y'], region['w'], region['h']

            # 基本的边界检查
            if w <= 0 or h <= 0 or x < 0 or y < 0:
                return None

            face_crop = frame[y:y + h, x:x + w]

            if face_crop.size == 0:
                return None

            blob = cv2.dnn.blobFromImage(face_crop, 1.0, (32, 32), (104.0, 177.0, 123.0))
            self.liveness_net.setInput(blob)
            preds = self.liveness_net.forward()

            is_live = preds[0][1] > preds[0][0]
            label = "Live" if is_live else "Spoof"

            return {"is_live": is_live, "label": label}
        except Exception as e:
            logger.warning(f"活体检测失败: {e}")
            return None
