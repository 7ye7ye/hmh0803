import asyncio
import logging
import cv2
import numpy as np
from deepface import DeepFace
import mediapipe as mp

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


class AdvancedLivenessChecker:
    def __init__(self, liveness_model_path: str):
        logger.info("正在初始化标准的活体检测分类模型...")
        self.liveness_model = cv2.dnn.readNetFromONNX(liveness_model_path)
        logger.info("正在初始化 MediaPipe Face Mesh 用于姿态分析...")
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.4
        )
        logger.info("高级活体检测方案初始化完成。")

    def _preprocess_liveness_input(self, face_crop: np.ndarray) -> np.ndarray:
        resized_face = cv2.resize(face_crop, (128, 128))
        blob = cv2.dnn.blobFromImage(resized_face, 1.0 / 255.0, (128, 128), mean=(0, 0, 0), swapRB=False, crop=False)
        return blob

    def check(self, frame: np.ndarray, face_region: dict) -> dict | None:
        """
        对指定的人脸区域进行多维度活体检测。
        返回: 包含模型分数和头部中心点位置的原始数据。
        """
        try:
            # 1. 从原始帧中裁剪出人脸
            x, y, w, h = face_region['x'], face_region['y'], face_region['w'], face_region['h']

            # 安全性检查，防止 face_region 坐标超出图像边界
            if x < 0 or y < 0 or x + w > frame.shape[1] or y + h > frame.shape[0]:
                logger.warning("提供的 face_region 超出图像边界，跳过本次检测。")
                return None

            face_crop = frame[y:y + h, x:x + w]
            if face_crop.size == 0:
                return None

            # 2. 模型检测 (这部分逻辑不变)
            liveness_input_blob = self._preprocess_liveness_input(face_crop)
            self.liveness_model.setInput(liveness_input_blob)
            preds = self.liveness_model.forward()
            model_confidence = preds[0][1] - preds[0][0]

            # 3. 头部中心点检测 (只在小的人脸切片上运行，效率更高)
            rgb_face_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_face_crop)

            face_center = None
            if results.multi_face_landmarks:
                # 获取在 face_crop 内的 landmark
                face_landmarks = results.multi_face_landmarks[0].landmark
                # 使用鼻子尖端作为稳定的面部中心点 (landmark 1)
                nose_tip = face_landmarks[1]

                # 将 face_crop 内的相对坐标，转换回 frame 内的绝对像素坐标
                h_crop, w_crop, _ = face_crop.shape
                abs_nose_x = x + (nose_tip.x * w_crop)
                abs_nose_y = y + (nose_tip.y * h_crop)

                # 最后，将绝对像素坐标转换回相对于整个 frame 的归一化坐标，用于位移计算
                h_frame, w_frame, _ = frame.shape
                face_center = (abs_nose_x / w_frame, abs_nose_y / h_frame)

            return {
                "model_confidence": model_confidence,
                "face_center": face_center
            }

        except Exception as e:
            logger.error(f"高级活体检测过程中发生错误: {e}", exc_info=True)
            return None