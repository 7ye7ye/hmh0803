import cv2
import asyncio
import logging
import time
import os
import numpy as np
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from deepface import DeepFace
from .utils import FaceEncoder, LivenessChecker

# --- 配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

VIDEO_STREAM_URL = "rtmp://120.46.210.148:1935/live/livestream"
MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = 'opencv'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIVENESS_MODEL_DIR = os.path.join(BASE_DIR, '..', 'models', 'liveness')
PROTOTXT_PATH = os.path.join(LIVENESS_MODEL_DIR, 'deploy.prototxt')
MODEL_PATH = os.path.join(LIVENESS_MODEL_DIR, 'liveness.model')

# 存储识别的实时信息
class FacialRecognitionService:
    def __init__(self):
        self.lock = asyncio.Lock()

        # 内部状态
        self.latest_frame: np.ndarray | None = None
        self.processed_frame: np.ndarray | None = None
        self.latest_result: dict = {}  # 存储向量、区域、活体等信息
        self.is_processing: bool = False  # 防止AI任务重叠

        # 初始化工具
        self.encoder = FaceEncoder(model_name=MODEL_NAME, detector_backend=DETECTOR_BACKEND)
        self.liveness_checker = LivenessChecker(prototxt_path=PROTOTXT_PATH, model_path=MODEL_PATH)

        # 统计信息
        self.stats = {
            "fps": 0.0,
            "last_detection_time": None,
            "faces_detected_session": 0
        }
        self._fps_start_time = time.time()
        self._fps_frame_count = 0

    async def start_background_tasks(self):
        """启动所有后台任务"""
        logger.info("启动后台任务: 视频流读取和AI处理...")
        asyncio.create_task(self._video_stream_loop())
        asyncio.create_task(self._ai_processing_loop())

    async def _video_stream_loop(self):
        """后台循环：从视频源读取帧。"""
        cap = cv2.VideoCapture(VIDEO_STREAM_URL)
        while True:
            if not cap.isOpened():
                logger.error(f"无法打开视频流: {VIDEO_STREAM_URL}，2秒后重试...")
                await asyncio.sleep(2)
                cap.release()
                cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                continue

            ret, frame = cap.read()
            if not ret:
                logger.warning("无法读取视频帧，将尝试重新连接。")
                cap.release()
                continue

            async with self.lock:
                self.latest_frame = frame

            # 更新FPS
            self._fps_frame_count += 1
            elapsed = time.time() - self._fps_start_time
            if elapsed >= 1.0:
                self.stats["fps"] = self._fps_frame_count / elapsed
                self._fps_start_time = time.time()
                self._fps_frame_count = 0

            await asyncio.sleep(1 / 60)  # 稍微让出CPU

    async def _ai_processing_loop(self):
        """后台循环：处理最新帧，进行人脸识别和活体检测。"""
        while True:
            if self.is_processing or self.latest_frame is None:
                await asyncio.sleep(0.05)
                continue

            try:
                self.is_processing = True

                async with self.lock:
                    frame_to_process = self.latest_frame.copy()

                # 1. 提取人脸向量
                face_data = await self.encoder.extract_vector(frame_to_process)

                # 复制一份用于绘制，避免修改原始帧
                display_frame = frame_to_process.copy()

                if face_data:
                    # 2. 如果检测到人脸，进行活体检测
                    region = face_data['region']
                    liveness_data = self.liveness_checker.check(frame_to_process, region)

                    if liveness_data:
                        # 合并所有结果
                        current_result = {**face_data, **liveness_data, "timestamp": time.time()}

                        # 绘制结果到显示帧上
                        (x, y, w, h) = (region['x'], region['y'], region['w'], region['h'])
                        label_color = (0, 255, 0) if liveness_data['is_live'] else (0, 0, 255)
                        cv2.rectangle(display_frame, (x, y), (x + w, y + h), label_color, 2)
                        cv2.putText(display_frame, liveness_data['label'], (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)

                        # 更新最新结果和统计数据
                        async with self.lock:
                            self.latest_result = current_result
                            self.stats["last_detection_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
                            self.stats["faces_detected_session"] += 1
                else:
                    # 未检测到人脸，清空旧结果
                    async with self.lock:
                        self.latest_result = {}

                # 更新用于视频流的已处理帧
                async with self.lock:
                    self.processed_frame = display_frame

            except Exception as e:
                logger.error(f"AI处理循环中发生错误: {e}", exc_info=True)
            finally:
                self.is_processing = False
                await asyncio.sleep(0.1)  # 每次处理后稍作休息

    async def get_video_stream(self):
        """生成用于web前端的视频流。"""
        while True:
            async with self.lock:
                # 优先使用处理过的帧，如果不存在（例如刚启动时），则使用原始帧
                frame = self.processed_frame if self.processed_frame is not None else self.latest_frame

            if frame is None:
                # 等待第一帧
                await asyncio.sleep(0.1)
                continue

            # 在帧上绘制FPS
            cv2.putText(frame, f"FPS: {self.stats['fps']:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            flag, encoded_image = cv2.imencode(".jpg", frame)
            if not flag:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')

            await asyncio.sleep(1 / 60)

    async def get_latest_face_info(self):
        """安全地获取最新的面部信息"""
        async with self.lock:
            return self.latest_result.copy()


# --- FastAPI 路由 ---
router = APIRouter(prefix="/ai/facial", tags=["facial"])

# 在应用启动时，创建 FacialRecognitionService 的实例，共享
facial_service = FacialRecognitionService()


@router.on_event("startup")
async def startup_event():
    """应用启动时，启动后台服务任务"""
    await facial_service.start_background_tasks()


@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(facial_service.get_video_stream(), media_type="multipart/x-mixed-replace; boundary=frame")


@router.get("/get_latest_vector")
async def get_latest_vector():
    result = await facial_service.get_latest_face_info()
    if result and result.get("vector_str"):
        return JSONResponse(content={
            "status": "success",
            "model": MODEL_NAME,
            "data": {
                "vector": result["vector_str"],
                "face_location": result["region"]
            }
        })
    else:
        return JSONResponse(status_code=404, content={"status": "error", "message": "暂无可用的人脸特征向量。"})