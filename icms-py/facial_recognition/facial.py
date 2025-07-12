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
VIDEO_STREAM_URL = 0
MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = 'opencv'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIVENESS_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'liveness_official', 'anti_spoof_predict.onnx')

class FacialRecognitionService:

    def __init__(self):
        self.lock = asyncio.Lock()
        self.latest_frame: np.ndarray | None = None
        self.processed_frame: np.ndarray | None = None
        self.latest_result: dict = {}
        self.is_processing: bool = False

        self.liveness_state = "CHECKING"  # 当前的活体认证状态，可以是 "CHECKING", "PASSED", "FAILED"
        self.liveness_history = deque(maxlen=10)  # 一个双端队列，用于存储最近10帧的活体判断结果 (True/False)
        self.position_history = deque(maxlen=5)  # 存储最近5帧的头部中心位置，用于计算位移
        self.MODEL_CONFIDENCE_THRESHOLD = 0.9  # AI模型判断为真人的置信度分数阈值，越高越严格
        self.STABLE_FRAME_REQUIREMENT = 6  # 需要连续多少帧判定为真人才算通过
        self.MOVEMENT_THRESHOLD = 0.002  # 头部中心点移动的最小距离阈值，用于区分静止照片

        # 创建人脸编码器实例，用于提取特征向量
        self.encoder = FaceEncoder(model_name=MODEL_NAME, detector_backend=DETECTOR_BACKEND)
        # 创建高级活体检测器实例，用于多维度活体判断
        self.liveness_checker = AdvancedLivenessChecker(liveness_model_path=LIVENESS_MODEL_PATH)

        self.stats = {"fps": 0.0}  # 简化后的统计信息，只关心最终输出的FPS

    # 启动两个主要的后台协程，让它们在程序运行期间持续工作。
    async def start_background_tasks(self):
        logger.info("启动后台任务: 视频流读取和AI处理...")
        # 创建并启动视频流读取任务
        asyncio.create_task(self._video_stream_loop())
        # 创建并启动AI处理任务
        asyncio.create_task(self._ai_processing_loop())

    # 视频流读取循环
    async def _video_stream_loop(self):
        cap = cv2.VideoCapture(VIDEO_STREAM_URL)
        while True:
            if not cap.isOpened():
                logger.error(f"无法打开视频流: {VIDEO_STREAM_URL}，2秒后重试...")
                await asyncio.sleep(2)
                cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                continue

            ret, frame = cap.read()
            if not ret:
                logger.warning("无法读取视频帧，可能流已中断，尝试重连...")
                await asyncio.sleep(2)
                cap.release()
                cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                continue

            async with self.lock:
                self.latest_frame = frame

            await asyncio.sleep(1 / 60)

    # 根据单帧的检测结果来更新整个认证状态。
    def _update_liveness_state(self, liveness_data: dict | None):
        current_frame_is_live = False

        if liveness_data:
            # 条件1: AI模型的置信度是否足够高
            model_ok = liveness_data["model_confidence"] > self.MODEL_CONFIDENCE_THRESHOLD

            # 条件2: 头部是否有微小运动（对抗照片攻击）
            movement_ok = False
            if liveness_data["face_center"]:
                self.position_history.append(liveness_data["face_center"])
                if len(self.position_history) > 1:
                    # 计算最近两帧的中心点在归一化坐标系中的欧氏距离
                    dx = self.position_history[-1][0] - self.position_history[-2][0]
                    dy = self.position_history[-1][1] - self.position_history[-2][1]
                    movement = (dx ** 2 + dy ** 2) ** 0.5
                    if movement > self.MOVEMENT_THRESHOLD:
                        movement_ok = True

            # 最终判定当前帧是否为“活体”：必须同时满足两个条件
            current_frame_is_live = model_ok and movement_ok

        #如果当前帧被判定为假，则立即清空所有历史记录，重置进度条
        if not current_frame_is_live:
            self.liveness_history.clear()
            self.position_history.clear()

        # 将当前帧的判断结果 (True/False) 加入历史记录队列
        self.liveness_history.append(current_frame_is_live)

        # 检查是否满足最终通过条件
        # 条件：历史记录队列已满 (即连续N帧) 并且 队列中所有的结果都为True
        if len(self.liveness_history) == self.liveness_history.maxlen and all(self.liveness_history):
            self.liveness_state = "PASSED"
        else:
            # 否则，状态保持/重置为“检查中”
            self.liveness_state = "CHECKING"

    async def _ai_processing_loop(self):
        while True:
            try:
                frame_to_process = None
                # 1. 安全地检查并获取待处理的帧
                async with self.lock:
                    if self.is_processing or self.latest_frame is None:
                        # 如果AI正在处理或没有新帧，则跳过本次循环
                        continue
                    self.is_processing = True
                    frame_to_process = self.latest_frame.copy()

                # 2. 统一由 DeepFace 进行人脸检测和向量提取
                face_data = await self.encoder.extract_vector(frame_to_process)
                display_frame = frame_to_process.copy()
                current_result = {}

                # 3. 如果 DeepFace 成功检测到人脸
                if face_data:
                    current_result.update(face_data)
                    region = face_data['region']

                    # 4. 对该人脸区域进行高级活体检测
                    liveness_data = self.liveness_checker.check(frame_to_process, region)

                    # 5. 根据检测结果，更新状态机
                    self._update_liveness_state(liveness_data)

                    # 6. 准备用于屏幕显示的状态文本和颜色
                    label_color = (0, 0, 255)  # 默认红色
                    status_text = "Checking Liveness..."
                    if self.liveness_state == "PASSED":
                        label_color = (0, 255, 0)  # 绿色
                        status_text = "Liveness Passed"

                    # 7. 绘制可视化元素
                    (x, y, w, h) = (region['x'], region['y'], region['w'], region['h'])
                    # 绘制人脸框
                    cv2.rectangle(display_frame, (x, y), (x + w, y + h), label_color, 2)
                    # 绘制状态文本
                    cv2.putText(display_frame, status_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)

                    # 绘制进度条，给用户实时反馈
                    live_frames_count = sum(self.liveness_history)
                    progress = live_frames_count / self.STABLE_FRAME_REQUIREMENT
                    cv2.rectangle(display_frame, (x, y + h + 5), (x + w, y + h + 15), (100, 100, 100), -1)

                    if progress > 0:
                        cv2.rectangle(display_frame, (x, y + h + 5), (int(x + w * progress), y + h + 15), (0, 255, 0),
                                      -1)
                else:
                    # 如果 DeepFace 未检测到人脸，则重置所有活体检测状态
                    self.liveness_history.clear()
                    self.position_history.clear()
                    self.liveness_state = "CHECKING"
                    # 并在屏幕上显示提示
                    cv2.putText(display_frame, "No Face Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                2)

                # --- 更新全局共享数据 ---
                async with self.lock:
                    if current_result:
                        current_result["liveness_passed"] = (self.liveness_state == "PASSED")
                        self.latest_result = current_result
                    else:
                        self.latest_result = {}

                    self.processed_frame = display_frame

            except Exception as e:
                logger.error(f"AI处理循环中发生错误: {e}", exc_info=True)
            finally:
                async with self.lock:
                    self.is_processing = False

                await asyncio.sleep(0.05)

    # 获取视频流
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
            cv2.putText(display_frame, f"FPS: {self.stats['fps']:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 255, 255), 2)

            # 将图像帧编码为JPEG格式
            flag, encoded_image = cv2.imencode(".jpg", display_frame)
            if not flag: continue

            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')

            await asyncio.sleep(1 / 60)


    async def get_latest_face_info(self):
        async with self.lock:
            return self.latest_result.copy()



router = APIRouter(prefix="/ai/facial", tags=["facial"])

facial_service = FacialRecognitionService()


@router.on_event("startup")
async def startup_event():
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