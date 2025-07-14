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

# 设置日志记录的基本配置，方便调试
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定义视频流地址、人脸识别模型等常量
VIDEO_STREAM_URL ="rtmp://120.46.210.148:1935/live/livestream"
MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = 'mtcnn'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIVENESS_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'liveness_official', 'anti_spoof_predict.onnx')


class FacialRecognitionService:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.latest_frame: np.ndarray | None = None
        self.processed_frame: np.ndarray | None = None
        self.latest_result: dict = {}

        # --- 活体检测相关状态 (核心修改) ---
        self.liveness_state = "CHECKING"  # 当前状态: CHECKING, PASSED
        self.vector_extracted = False
        self.is_processing: bool = False
        self.liveness_history = deque(maxlen=20)
        self.position_history = deque(maxlen=5)

        # --- 新增的状态变量 ---
        self.verification_timestamp = 0  # 记录验证成功的时间戳
        self.SUCCESS_DISPLAY_DURATION = 3  # 成功状态显示3秒

        # --- 阈值和常量 ---
        self.MODEL_CONFIDENCE_THRESHOLD = 0.7
        self.STABLE_FRAME_REQUIREMENT = 3
        self.MOVEMENT_THRESHOLD = 0.0008

        # 初始化组件
        self.encoder = FaceEncoder(model_name=MODEL_NAME, detector_backend=DETECTOR_BACKEND)
        self.liveness_checker = AdvancedLivenessChecker(liveness_model_path=LIVENESS_MODEL_PATH)

        self.stats = {"fps": 0.0, "process_fps": 0.0}

    async def start_background_tasks(self):
        """启动后台任务: 视频流读取和AI处理"""
        logger.info("启动后台任务: 视频流读取和AI处理...")
        try:
            self.video_task = asyncio.create_task(self._video_stream_loop())
            self.ai_task = asyncio.create_task(self._ai_processing_loop())
            logger.info("后台任务启动成功")
        except Exception as e:
            logger.error(f"启动后台任务时发生错误: {e}")
            raise

    async def _video_stream_loop(self):
        cap = cv2.VideoCapture(VIDEO_STREAM_URL)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        while True:
            if not cap.isOpened():
                logger.error(f"无法打开视频流: {VIDEO_STREAM_URL}，2秒后重试...")
                async with self.lock:
                    if self.latest_result:
                        self.latest_result.clear()
                self.reset_state()
                await asyncio.sleep(2)
                cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                continue

            ret, frame = cap.read()
            if not ret:
                logger.warning("无法读取视频帧，可能流已中断，尝试重连...")
                async with self.lock:
                    if self.latest_result:
                        self.latest_result.clear()
                self.reset_state()
                cap.release()
                await asyncio.sleep(2)
                cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                continue

            async with self.lock:
                self.latest_frame = frame
            await asyncio.sleep(1 / 60)

    # --- reset_state 方法修改 ---
    def reset_state(self):
        """重置所有状态，为下一次检测做准备"""
        self.liveness_state = "CHECKING"
        self.vector_extracted = False
        self.liveness_history.clear()
        self.position_history.clear()
        self.verification_timestamp = 0  # 重置时间戳
        logger.debug("活体检测过程状态已重置，准备进行下一轮检测。")

    def _update_liveness_state(self, liveness_data: dict | None, region: dict, frame_shape: tuple):
        # 此方法逻辑保持不变，它只负责判断是否应该进入 "PASSED" 状态
        current_frame_is_live = False
        model_ok = False
        movement_ok = False
        movement = 0.0
        model_score = -99.0

        h_frame, w_frame, _ = frame_shape
        cx = region.get('x', 0) + region.get('w', 0) / 2
        cy = region.get('y', 0) + region.get('h', 0) / 2
        face_center = (cx / w_frame, cy / h_frame)
        self.position_history.append(face_center)

        if liveness_data:
            model_score = liveness_data['model_confidence']
            model_ok = model_score > self.MODEL_CONFIDENCE_THRESHOLD

        if len(self.position_history) > 1:
            p1 = self.position_history[-1]
            p2 = self.position_history[-2]
            if p1 and p2:
                dx = p1[0] - p2[0]
                dy = p1[1] - p2[1]
                movement = (dx ** 2 + dy ** 2) ** 0.5
                movement_ok = movement > self.MOVEMENT_THRESHOLD

        current_frame_is_live = model_ok and movement_ok

        logger.info(
            f"Liveness Check: "
            f"Model OK? {model_ok} (Score: {model_score:.4f}), "
            f"Movement OK? {movement_ok} (Move: {movement:.6f}), "
            f"--> Current Frame Live: {current_frame_is_live}"
        )

        if not current_frame_is_live:
            self.liveness_history.clear()
        else:
            self.liveness_history.append(True)  # 只在活体时添加记录

        progress = len(self.liveness_history)  # 修改进度计算方式
        logger.info(f"Liveness Progress: {progress}/{self.STABLE_FRAME_REQUIREMENT}")

        # --- 状态转换逻辑 ---
        # 注意: 这里不再直接修改 self.liveness_state，而是返回是否通过
        if len(self.liveness_history) >= self.STABLE_FRAME_REQUIREMENT:
            if self.liveness_state != "PASSED":
                logger.info("✅ Liveness Passed!")
            self.liveness_state = "PASSED"

    # --- _ai_processing_loop 方法核心修改 ---
    async def _ai_processing_loop(self):
        process_start_time = time.time()
        process_count = 0

        while True:
            frame_to_process = None
            async with self.lock:
                if self.latest_frame is None:
                    await asyncio.sleep(0.02)
                    continue
                frame_to_process = self.latest_frame.copy()

            display_frame = frame_to_process.copy()

            try:
                # 步骤 1: 检查是否处于成功展示期，如果超时则重置
                if self.liveness_state == "PASSED" and time.time() - self.verification_timestamp > self.SUCCESS_DISPLAY_DURATION:
                    logger.info(f"成功状态展示超过 {self.SUCCESS_DISPLAY_DURATION} 秒，重置系统。")
                    self.reset_state()
                    async with self.lock:
                        if self.latest_result: self.latest_result.clear()

                # 步骤 2: 检测人脸
                detected_faces = await asyncio.to_thread(
                    DeepFace.extract_faces,
                    img_path=frame_to_process,
                    detector_backend=DETECTOR_BACKEND,
                    enforce_detection=False
                )

                if detected_faces:
                    main_face = detected_faces[0]
                    region = main_face['facial_area']

                    # 步骤 3: 核心状态机逻辑
                    if self.liveness_state == "CHECKING":
                        # 状态A: 正在进行活体检测
                        liveness_data = self.liveness_checker.check(frame_to_process, region)
                        self._update_liveness_state(liveness_data, region, frame_to_process.shape)

                    if self.liveness_state == "PASSED" and not self.vector_extracted:
                        # 状态B: 活体检测刚通过，且尚未提取向量
                        logger.info("活体检测通过，正在提取特征向量...")
                        face_crop = main_face['face']
                        face_data = await self.encoder.extract_vector(face_crop)

                        if face_data:
                            logger.info("特征向量提取成功！更新结果并进入'成功展示'模式。")
                            self.vector_extracted = True  # 标记向量已提取
                            self.verification_timestamp = time.time()  # 记录成功时间
                            async with self.lock:
                                self.latest_result = face_data
                                self.latest_result["liveness_passed"] = True
                        else:
                            logger.warning("活体通过了，但特征提取失败，重置状态。")
                            self.reset_state()

                    # 步骤 4: 无论在哪个状态，都绘制可视化框
                    self._draw_visualization(display_frame, region)

                else:
                    # 步骤 5: 如果未检测到人脸，重置所有状态
                    if self.liveness_state == "PASSED" or self.latest_result:
                        logger.info("人脸从画面消失，已清除之前的有效结果并重置状态。")
                        async with self.lock:
                            if self.latest_result: self.latest_result.clear()
                        self.reset_state()

                    cv2.putText(display_frame, "No Face Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                2)

                # 更新FPS和处理后的帧
                process_count += 1
                elapsed = time.time() - process_start_time
                if elapsed >= 1.0:
                    self.stats['process_fps'] = process_count / elapsed
                    process_start_time = time.time()
                    process_count = 0

                async with self.lock:
                    self.processed_frame = display_frame

            except Exception as e:
                logger.error(f"AI处理循环中发生错误: {e}", exc_info=True)
                self.reset_state()

            await asyncio.sleep(0.033)

    def _draw_visualization(self, frame: np.ndarray, region: dict):
        label_color = (0, 0, 255)  # 默认红色 (CHECKING)
        status_text = "Checking Liveness..."
        progress = len(self.liveness_history) / self.STABLE_FRAME_REQUIREMENT

        if self.liveness_state == "PASSED":
            label_color = (0, 255, 0)  # 绿色 (PASSED)
            if self.vector_extracted:
                status_text = "Verification Ready"
            else:
                # 这个状态很短暂，但可能出现
                status_text = "Liveness Passed"
            progress = 1.0  # 通过后进度条直接拉满

        x, y, w, h = region['x'], region['y'], region['w'], region['h']
        cv2.rectangle(frame, (x, y), (x + w, y + h), label_color, 2)
        cv2.putText(frame, status_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)

        # 绘制进度条
        cv2.rectangle(frame, (x, y + h + 5), (x + w, y + h + 15), (100, 100, 100), -1)
        if progress > 0:
            cv2.rectangle(frame, (x, y + h + 5), (int(x + w * progress), y + h + 15), (0, 255, 0), -1)

    # --- get_video_stream 和 get_latest_face_info 方法保持不变 ---
    async def get_video_stream(self):
        fps_start_time = time.time()
        fps_frame_count = 0
        while True:
            display_frame = None
            async with self.lock:
                # 优先使用处理过的帧，如果不存在（例如刚启动时），则使用原始帧
                display_frame = self.processed_frame if self.processed_frame is not None else self.latest_frame

            if display_frame is None:
                await asyncio.sleep(0.1)
                continue

            fps_frame_count += 1
            elapsed_time = time.time() - fps_start_time
            if elapsed_time >= 1.0:
                self.stats['fps'] = fps_frame_count / elapsed_time
                fps_start_time = time.time()
                fps_frame_count = 0

            # 在帧上绘制FPS信息
            cv2.putText(display_frame, f"Display FPS: {self.stats['fps']:.1f}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(display_frame, f"Process FPS: {self.stats['process_fps']:.1f}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # 将图像帧编码为JPEG格式
            flag, encoded_image = cv2.imencode(".jpg", display_frame,
                                               [cv2.IMWRITE_JPEG_QUALITY, 80])
            if not flag:
                continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')

            await asyncio.sleep(1 / 25)

    async def get_latest_face_info(self):
        async with self.lock:
            return self.latest_result.copy()



router = APIRouter(prefix="/ai/facial", tags=["facial"])
facial_service = FacialRecognitionService()


@router.on_event("startup")
async def startup_event():
    """服务启动时的初始化"""
    try:
        logger.info("正在初始化人脸识别服务...")
        await facial_service.start_background_tasks()
        logger.info("人脸识别服务初始化完成")
    except Exception as e:
        logger.error(f"初始化人脸识别服务时发生错误: {e}")
        raise

@router.on_event("shutdown")
async def shutdown_event():
    """服务关闭时的清理"""
    try:
        logger.info("正在关闭人脸识别服务...")
        await facial_service.cleanup()
        logger.info("人脸识别服务已关闭")
    except Exception as e:
        logger.error(f"关闭人脸识别服务时发生错误: {e}")


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