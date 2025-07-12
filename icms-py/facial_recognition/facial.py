import cv2
import asyncio
import logging
import time
import os
import numpy as np
from collections import deque
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from deepface import DeepFace
from .utils import FaceEncoder, AdvancedLivenessChecker

# --- 配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

VIDEO_STREAM_URL = "rtmp://120.46.210.148:1935/live/livestream"
MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = 'opencv'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIVENESS_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'liveness_official', 'anti_spoof_predict.onnx')

# 存储识别的实时信息
class FacialRecognitionService:
    def __init__(self):
        self.lock = asyncio.Lock()
        # --- 基础状态 ---
        self.latest_frame: np.ndarray | None = None
        self.processed_frame: np.ndarray | None = None
        self.latest_result: dict = {}
        self.is_processing: bool = False

        # --- 高级活体检测状态机 ---
        self.liveness_state = "CHECKING"  # CHECKING, PASSED, FAILED
        self.liveness_history = deque(maxlen=15)  # 存储最近15帧的检测结果
        self.position_history = deque(maxlen=5)  # 存储最近5帧的头部中心位置

        # --- 状态机阈值 (可调参数) ---
        self.MODEL_CONFIDENCE_THRESHOLD = 1.0  # 模型判断为真人的置信度阈值，可以调高更严格（1.2 1.0）
        self.STABLE_FRAME_REQUIREMENT = 8  # 需要连续多少帧判定为真人才算通过
        self.MOVEMENT_THRESHOLD = 0.003  # 头部中心点移动阈值，用于判断是否是静止照片

        # 初始化工具
        self.encoder = FaceEncoder(model_name=MODEL_NAME, detector_backend=DETECTOR_BACKEND)
        self.liveness_checker = AdvancedLivenessChecker(liveness_model_path=LIVENESS_MODEL_PATH)

        # 更新相关信息统计
        self.stats = {"fps": 0.0, "last_detection_time": None, "faces_detected_session": 0}
        self._fps_start_time = time.time()
        self._fps_frame_count = 0

    async def start_background_tasks(self):
        logger.info("启动后台任务: 视频流读取和AI处理...")
        asyncio.create_task(self._video_stream_loop())
        asyncio.create_task(self._ai_processing_loop())

    async def _video_stream_loop(self):
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
                await asyncio.sleep(2)
                cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                continue
            async with self.lock:
                self.latest_frame = frame.copy()
            await asyncio.sleep(1 / 60)

    def _update_liveness_state(self, liveness_data: dict | None):

        # 状态机默认当前帧为假
        current_frame_is_live = False

        if liveness_data:
            # 1. 检查模型置信度
            model_ok = liveness_data["model_confidence"] > self.MODEL_CONFIDENCE_THRESHOLD

            # 2. 检查头部微小运动
            movement_ok = False
            if liveness_data["face_center"]:
                self.position_history.append(liveness_data["face_center"])
                if len(self.position_history) > 1:
                    # 计算最近两帧的中心点位移
                    dx = self.position_history[-1][0] - self.position_history[-2][0]
                    dy = self.position_history[-1][1] - self.position_history[-2][1]
                    movement = (dx ** 2 + dy ** 2) ** 0.5
                    if movement > self.MOVEMENT_THRESHOLD:
                        movement_ok = True

            # 当前帧判定为真人的条件：模型通过 且 有微小移动
            current_frame_is_live = model_ok and movement_ok

        # 将当前帧的结果加入历史记录
        self.liveness_history.append(current_frame_is_live)

        # 如果历史记录中有任何一帧为假，就重置状态为 CHECKING
        if not all(self.liveness_history):
            self.liveness_state = "CHECKING"

        # 只有当历史记录满了，并且所有帧都为真时，才认证通过
        if len(self.liveness_history) == self.liveness_history.maxlen and all(self.liveness_history):
            self.liveness_state = "PASSED"

    async def _ai_processing_loop(self):
        while True:
            frame_to_process = None
            should_process = False

            # 1. 安全地检查并获取帧
            async with self.lock:
                if not self.is_processing and self.latest_frame is not None:
                    self.is_processing = True
                    frame_to_process = self.latest_frame.copy()
                    should_process = True

            # 2. 如果没有可处理的帧，等待一段时间
            if not should_process:
                await asyncio.sleep(0.05)
                continue

            try:
                # 3. AI处理逻辑（在锁外执行，避免阻塞）
                # 统一由 DeepFace 进行人脸检测和向量提取
                face_data = await self.encoder.extract_vector(frame_to_process)
                display_frame = frame_to_process.copy()
                current_result = {}

                if face_data:
                    current_result.update(face_data)
                    region = face_data['region']
                    (x, y, w, h) = (region['x'], region['y'], region['w'], region['h'])

                    # 对检测到的人脸区域进行高级活体检测
                    liveness_data = self.liveness_checker.check(frame_to_process, region)

                    # 更新状态机
                    self._update_liveness_state(liveness_data)

                    # 效果展示
                    label_color = (0, 0, 255)  # 默认红色 (失败/检查中)
                    status_text = "Spoof Detected or Checking..."
                    if self.liveness_state == "PASSED":
                        label_color = (0, 255, 0)  # 绿色
                        status_text = "Liveness Passed"

                    # 绘制进度条，给用户反馈
                    live_frames_count = sum(1 for live in self.liveness_history if live)
                    progress = min(live_frames_count / self.STABLE_FRAME_REQUIREMENT, 1.0)  # 确保不超过1.0

                    # 绘制进度条背景
                    cv2.rectangle(display_frame, (x, y + h + 5), (x + w, y + h + 15), (100, 100, 100), -1)
                    # 绘制进度条
                    if progress > 0:
                        cv2.rectangle(display_frame, (x, y + h + 5), (int(x + w * progress), y + h + 15), label_color,
                                      -1)

                    # 绘制人脸框和状态文本
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), label_color, 2)
                    cv2.putText(display_frame, status_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)

                    # 添加进度信息
                    progress_text = f"Progress: {live_frames_count}/{self.STABLE_FRAME_REQUIREMENT}"
                    cv2.putText(display_frame, progress_text, (x, y + h + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (255, 255, 255), 1)
                else:
                    # 如果没检测到人脸，清空历史记录，重置状态
                    self.liveness_history.clear()
                    self.position_history.clear()
                    self.liveness_state = "CHECKING"

                    # 在显示帧上添加提示
                    cv2.putText(display_frame, "No face detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                2)

                # 4. 更新全局状态（需要在锁内进行）
                async with self.lock:
                    if current_result:
                        current_result["liveness_passed"] = (self.liveness_state == "PASSED")
                        self.latest_result = current_result
                    self.processed_frame = display_frame

                    # 更新FPS统计
                    self._update_fps_stats()

            except Exception as e:
                logger.error(f"AI处理循环中发生错误: {e}", exc_info=True)
                # 发生错误时，确保显示一个错误帧
                try:
                    error_frame = frame_to_process.copy() if frame_to_process is not None else np.zeros((480, 640, 3),
                                                                                                        dtype=np.uint8)
                    cv2.putText(error_frame, f"Processing Error: {str(e)[:50]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                0.7, (0, 0, 255), 2)
                    async with self.lock:
                        self.processed_frame = error_frame
                except:
                    pass  # 如果连错误帧都无法创建，就忽略
            finally:
                # 5. 确保释放处理标志
                async with self.lock:
                    self.is_processing = False

                # 6. 短暂等待，避免CPU过度占用
                await asyncio.sleep(0.1)

    def _update_fps_stats(self):
        """更新FPS统计"""
        current_time = time.time()
        self._fps_frame_count += 1

        # 每秒更新一次FPS
        if current_time - self._fps_start_time >= 1.0:
            self.stats["fps"] = self._fps_frame_count / (current_time - self._fps_start_time)
            self._fps_frame_count = 0
            self._fps_start_time = current_time


    async def get_video_stream(self):
        while True:
            async with self.lock:
                frame = self.processed_frame if self.processed_frame is not None else self.latest_frame
            if frame is None: await asyncio.sleep(0.1); continue
            cv2.putText(frame, f"FPS: {self.stats['fps']:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255),
                        2)
            flag, encoded_image = cv2.imencode(".jpg", frame)
            if not flag: continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')
            await asyncio.sleep(1 / 60)

    async def get_latest_face_info(self):
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