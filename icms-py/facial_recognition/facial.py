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
DETECTOR_BACKEND = 'opencv'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIVENESS_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'liveness_official', 'anti_spoof_predict.onnx')

class FacialRecognitionService:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.latest_frame: np.ndarray | None = None
        self.processed_frame: np.ndarray | None = None
        self.latest_result: dict = {}

        #活体检测相关状态
        self.liveness_state = "CHECKING"
        self.is_processing: bool = False
        self.liveness_history = deque(maxlen=10)
        self.position_history = deque(maxlen=5)
        self.MODEL_CONFIDENCE_THRESHOLD = 0.9
        self.STABLE_FRAME_REQUIREMENT = 6
        self.MOVEMENT_THRESHOLD = 0.002

        # # 性能优化相关
        # self.last_process_time = 0
        # self.process_interval = 0.1   #每100ms处理一次，不是每帧都处理
        # self.skip_frames = 0
        # self.max_skip_frames = 3   #最多跳过三帧


        # 初始化组件
        self.encoder = FaceEncoder(model_name=MODEL_NAME, detector_backend=DETECTOR_BACKEND)
        self.liveness_checker = AdvancedLivenessChecker(liveness_model_path=LIVENESS_MODEL_PATH)

        self.stats = {"fps": 0.0,"process_fps":0.0}  # 简化后的统计信息，只关心最终输出的FPS

    async def start_background_tasks(self):
        logger.info("启动后台任务: 视频流读取和AI处理...")
        asyncio.create_task(self._video_stream_loop())
        asyncio.create_task(self._ai_processing_loop())

    # 视频流读取循环
    async def _video_stream_loop(self):
        cap = cv2.VideoCapture(VIDEO_STREAM_URL)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        while True:
            if not cap.isOpened():
                logger.error(f"无法打开视频流: {VIDEO_STREAM_URL}，2秒后重试...")
                await asyncio.sleep(2)
                cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                continue
            ret, frame = cap.read()
            if not ret:
                logger.warning("无法读取视频帧，可能流已中断，尝试重连...")
                cap.release()
                await asyncio.sleep(2)
                cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                continue
            async with self.lock:
                self.latest_frame = frame
            await asyncio.sleep(1 / 60)  # 保持高读取率，让AI循环自己决定处理频率

        def reset_state(self):
            self.liveness_state = "CHECKING"
            self.vector_extracted = False
            self.liveness_history.clear()
            self.position_history.clear()
            self.latest_result = {}
            logger.debug("认证状态已重置。")

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
                    movement_ok = movement > self.MOVEMENT_THRESHOLD

            # 最终判定当前帧是否为“活体”：必须同时满足两个条件
            current_frame_is_live = model_ok and movement_ok

        #如果当前帧被判定为假，则立即清空所有历史记录，重置进度条
        if not current_frame_is_live:
            self.liveness_history.clear()
            self.position_history.clear()

        # 将当前帧的判断结果 (True/False) 加入历史记录队列
        self.liveness_history.append(current_frame_is_live)

        # 检查是否满足最终通过条件，连续6帧通过才是true
        if len(self.liveness_history) == self.liveness_history.maxlen and all(self.liveness_history):
            self.liveness_state = "PASSED"
            logger.info("活体检测已通过！")
        else:
            self.liveness_state = "CHECKING"

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
                # 步骤 1: 使用快速的人脸检测器，而不是完整的 represent
                # DeepFace.extract_faces 只做检测和裁剪，速度快得多
                detected_faces = await asyncio.to_thread(
                    DeepFace.extract_faces,
                    img_path=frame_to_process,
                    detector_backend=DETECTOR_BACKEND,
                    enforce_detection=False  # 未检测到脸时返回空列表
                )

                if detected_faces:
                    main_face = detected_faces[0]  # 只处理最大的人脸
                    region = main_face['facial_area']

                    # 步骤 2: 只要还没提取向量，就持续进行活体检测
                    if not self.vector_extracted:
                        liveness_data = self.liveness_checker.check(frame_to_process, region)
                        self._update_liveness_state(liveness_data)

                    # 步骤 3: 如果活体检测通过 且 尚未提取向量，则执行一次性慢速操作
                    if self.liveness_state == "PASSED" and not self.vector_extracted:
                        logger.info("活体检测通过，正在提取特征向量...")
                        # 在人脸切片上提取特征，而不是全图，效率更高
                        face_crop = main_face['face']

                        face_data = await self.encoder.extract_vector(face_crop)

                        if face_data:
                            logger.info("特征向量提取成功！")
                            async with self.lock:
                                self.latest_result = face_data
                                self.latest_result["liveness_passed"] = True
                            self.vector_extracted = True  # 标记为已提取，不再重复此操作
                        else:
                            logger.warning("活体通过了，但特征提取失败，重置状态。")
                            self.reset_state()

                    # 步骤 4: 绘制可视化界面
                    self._draw_visualization(display_frame, region)

                else:  # 如果未检测到人脸
                    self.reset_state()
                    cv2.putText(display_frame, "No Face Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                2)

                # 更新统计信息
                process_count += 1
                elapsed = time.time() - process_start_time
                if elapsed >= 1.0:
                    self.stats['process_fps'] = process_count / elapsed
                    process_start_time = time.time()
                    process_count = 0

                # 更新用于推流的帧
                async with self.lock:
                    self.processed_frame = display_frame

            except Exception as e:
                logger.error(f"AI处理循环中发生错误: {e}", exc_info=True)

            await asyncio.sleep(0.033)  # 约等于30FPS的处理频率

    def _draw_visualization(self, frame: np.ndarray, region: dict):
        label_color = (0, 0, 255)  # 默认红色
        status_text = "Checking Liveness..."
        if self.liveness_state == "PASSED":
            label_color = (0, 255, 0)  # 绿色
            status_text = "Liveness Passed"
            if self.vector_extracted:
                status_text = "Verification Ready"

        x, y, w, h = region['x'], region['y'], region['w'], region['h']
        cv2.rectangle(frame, (x, y), (x + w, y + h), label_color, 2)
        cv2.putText(frame, status_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, label_color, 2)

        progress = sum(self.liveness_history) / self.STABLE_FRAME_REQUIREMENT
        cv2.rectangle(frame, (x, y + h + 5), (x + w, y + h + 15), (100, 100, 100), -1)
        if progress > 0:
            cv2.rectangle(frame, (x, y + h + 5), (int(x + w * progress), y + h + 15), (0, 255, 0), -1)

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