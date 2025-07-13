import asyncio
import logging
import cv2
import numpy as np
from deepface import DeepFace
import base64
#import mediapipe as mp
from threading import Lock
import time


logger = logging.getLogger(__name__)


class FaceEncoder:
    """负责从图像帧中提取人脸特征向量。"""
    def __init__(self, model_name: str, detector_backend: str):
        self.model_name = model_name
        self.detector_backend = detector_backend
        self._model_lock = Lock()
        self._model_loaded = False

        # 预加载模型以提高后续性能
        logger.info(f"正在为 FaceEncoder 预加载模型 '{model_name}'...")
        try:
            DeepFace.build_model(model_name)
            self._model_loaded = True
            logger.info("FaceEncoder 模型预加载完成。")
        except Exception as e:
            logger.error(f"模型预加载失败：{e}")

    async def extract_vector(self, frame: np.ndarray) -> dict | None:
        """
        从单帧图像中提取人脸信息。
        返回: 一个包含向量、区域等信息的字典，如果未检测到则返回 None。
        """
        if frame is None or frame.size == 0 or not self._model_loaded:
            return None
        try:
            # 线程执行器来运行cpu密集型任务
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._extract_face_sync,
                frame

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
            logger.debug("在帧中未检测到人脸。")
            return None
        except Exception as e:
            logger.warning(f"向量提取过程中发生未知错误: {e}")
            return None
    def _extract_face_sync(self,frame:np.ndarray):
        with self._model_lock:
            return DeepFace.represent(
                img_path=frame,
                model_name=self.model_name,
                detector_backend='skip',
                enforce_detection=False
            )
    
    @staticmethod
    def extract_vector_from_image(image_str: str, model_name: str = "Facenet512", detector_backend: str = "opencv") -> dict | None:
        """
        从base64编码的图像字符串中提取人脸特征向量。
        
        Args:
            image_str: base64编码的图像字符串
            model_name: 使用的模型名称，默认为Facenet512
            detector_backend: 使用的检测器后端，默认为opencv
            
        Returns:
            dict: 包含向量信息的字典，如果失败则返回None
            {
                "vector_list": list,  # 人脸特征向量列表
                "vector_str": str,    # 逗号分隔的向量字符串
                "region": dict        # 人脸区域信息
            }
        """
        try:
            # 1. 解码base64图像字符串
            if "base64," in image_str:
                image_str = image_str.split("base64,")[1]
            
            img_data = base64.b64decode(image_str)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error("无法解码图像数据")
                return None
                
            # 2. 使用DeepFace提取特征向量
            results = DeepFace.represent(
                img_path=frame,
                model_name=model_name,
                detector_backend=detector_backend,
                enforce_detection=True  # 强制检测人脸
            )
            
            if not results or len(results) == 0:
                logger.warning("未在图像中检测到人脸")
                return None
                
            # 3. 处理结果
            face_info = results[0]
            vector = face_info['embedding']
            vector_str = ",".join(map(str, vector))
            
            return {
                "vector_list": vector,
                "vector_str": vector_str,
                "region": face_info['facial_area']
            }
            
        except ValueError as ve:
            logger.warning(f"人脸检测失败: {ve}")
            return None
        except Exception as e:
            logger.error(f"处理图像时发生错误: {e}")
            return None
            
    


class AdvancedLivenessChecker:
    def __init__(self, liveness_model_path: str):
        logger.info("正在初始化标准的活体检测分类模型...")
        self.liveness_model = cv2.dnn.readNetFromONNX(liveness_model_path)
        logger.info("活体检测方案初始化完成 (仅模型检测)。")

    def _preprocess_liveness_input(self, face_crop: np.ndarray) -> np.ndarray:
        resized_face = cv2.resize(face_crop, (128, 128))
        blob = cv2.dnn.blobFromImage(resized_face, 1.0 / 255.0, (128, 128), mean=(0, 0, 0), swapRB=False, crop=False)
        return blob

    def check(self, frame: np.ndarray, face_region: dict) -> dict | None:
        """
        对指定的人脸区域进行活体检测。
        返回: 仅包含模型分数的原始数据。中心点检测逻辑已移除。
        """
        try:
            # 1. 从原始帧中裁剪出人脸
            x, y, w, h = face_region['x'], face_region['y'], face_region['w'], face_region['h']

            if x < 0 or y < 0 or x + w > frame.shape[1] or y + h > frame.shape[0]:
                logger.warning("提供的 face_region 超出图像边界，跳过本次检测。")
                return None

            face_crop = frame[y:y + h, x:x + w]
            if face_crop.size == 0:
                return None

            # 2. 模型检测
            liveness_input_blob = self._preprocess_liveness_input(face_crop)
            self.liveness_model.setInput(liveness_input_blob)
            preds = self.liveness_model.forward()
            model_confidence = preds[0][1] - preds[0][0]

            return {
                "model_confidence": model_confidence

            }

        except Exception as e:
            logger.error(f"活体检测过程中发生错误: {e}", exc_info=True)
            return None
