import cv2
import asyncio
import logging
import time
import os
import numpy as np
from collections import deque
from fastapi import APIRouter
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse
from deepface import DeepFace
from .utils import FaceEncoder, AdvancedLivenessChecker, MouthOpeningDetector

# 设置日志记录的基本配置，方便调试
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定义视频流地址、人脸识别模型等常量
VIDEO_STREAM_URL ="rtmp://121.36.44.77:1935/live/livestream"
MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = 'mtcnn'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIVENESS_MODEL_PATH = os.path.join(BASE_DIR, '..', 'models', 'liveness_official', 'anti_spoof_predict.onnx')
# 定义路由
router = APIRouter(prefix="/ai/facial", tags=["Facial"])


class FacialRecognitionService:
    def __init__(self):
        self.lock = asyncio.Lock()
        self.latest_frame: np.ndarray | None = None
        self.processed_frame: np.ndarray | None = None
        self.latest_result: dict = {}
        self.is_running = False
        self.video_task = None
        self.ai_task = None
        self.cap = None

        # 活体检测相关状态
        self.liveness_state = "CHECKING"  # 当前状态: CHECKING, PASSED
        self.vector_extracted = False
        self.is_processing: bool = False
        self.liveness_history = deque(maxlen=10)
        self.position_history = deque(maxlen=5)
        self.verification_timestamp = 0  # 记录验证成功的时间戳
        self.SUCCESS_DISPLAY_DURATION = 3  # 成功状态显示3秒

        # --- 阈值和常量 ---
        self.MODEL_CONFIDENCE_THRESHOLD = 0.7
        self.STABLE_FRAME_REQUIREMENT = 10
        self.MOVEMENT_THRESHOLD = 0.0008
        self.PASSIVE_STABILITY_REQUIREMENT = 5  # 需要5帧稳定才进入下一阶段
        self.MOUTH_OPEN_THRESHOLD = 0.35  # 嘴巴张开比例阈值，需要根据实际情况微调
        self.SUCCESS_DISPLAY_DURATION = 3

        # 初始化组件
        self.encoder = FaceEncoder(model_name=MODEL_NAME, detector_backend=DETECTOR_BACKEND)
        self.liveness_checker = AdvancedLivenessChecker(liveness_model_path=LIVENESS_MODEL_PATH)
        self.mouth_detector = MouthOpeningDetector()
        self.stats = {"fps": 0.0, "process_fps": 0.0}

    async def start_analysis(self):
        """按需启动视频流分析"""
        if self.is_running:
            return
        
        logger.info("启动视频流分析...")
        self.is_running = True
        self.reset_state()
        
        try:
            self.video_task = asyncio.create_task(self._video_stream_loop())
            self.ai_task = asyncio.create_task(self._ai_processing_loop())
            logger.info("视频流分析启动成功")
        except Exception as e:
            logger.error(f"启动视频流分析时发生错误: {e}")
            await self.stop_analysis()
            raise

    async def stop_analysis(self):
        """停止视频流分析"""
        logger.info("正在停止视频流分析...")
        self.is_running = False
        
        # 取消后台任务
        if self.video_task:
            self.video_task.cancel()
            try:
                await self.video_task
            except asyncio.CancelledError:
                pass
            self.video_task = None
            
        if self.ai_task:
            self.ai_task.cancel()
            try:
                await self.ai_task
            except asyncio.CancelledError:
                pass
            self.ai_task = None
            
        # 释放摄像头资源
        if self.cap:
            self.cap.release()
            self.cap = None
            
        # 清理状态
        self.latest_frame = None
        self.processed_frame = None
        self.latest_result.clear()
        logger.info("视频流分析已停止")

    async def _video_stream_loop(self):
        """视频流读取循环"""
        self.cap = cv2.VideoCapture(VIDEO_STREAM_URL)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        while self.is_running:
            if not self.cap.isOpened():
                logger.error(f"无法打开视频流: {VIDEO_STREAM_URL}，2秒后重试...")
                async with self.lock:
                    if self.latest_result:
                        self.latest_result.clear()
                self.reset_state()
                await asyncio.sleep(2)
                if not self.is_running:
                    break
                self.cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                continue

            ret, frame = self.cap.read()
            if not ret:
                logger.warning("无法读取视频帧，可能流已中断，尝试重连...")
                async with self.lock:
                    if self.latest_result:
                        self.latest_result.clear()
                self.reset_state()
                self.cap.release()
                await asyncio.sleep(2)
                if not self.is_running:
                    break
                self.cap = cv2.VideoCapture(VIDEO_STREAM_URL)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                continue

            async with self.lock:
                self.latest_frame = frame
            await asyncio.sleep(1/60)

    def reset_state(self):
        """重置所有状态，为下一次检测做准备"""
        self.liveness_state = "CHECKING"
        self.vector_extracted = False
        self.liveness_history.clear()
        self.position_history.clear()
        self.verification_timestamp = 0  # 重置时间戳
        self.passive_check_stable_frames = 0  # 重置稳定帧计数
        logger.debug("活体检测过程状态已重置，准备进行下一轮检测。")

    def _update_passive_check_state(self, liveness_data: dict | None, region: dict, frame_shape: tuple) -> bool:
        """执行被动检测（模型+移动），返回当前帧是否通过。"""
        model_ok = False
        if liveness_data and liveness_data['model_confidence'] > self.MODEL_CONFIDENCE_THRESHOLD:
            model_ok = True

        h_frame, w_frame, _ = frame_shape
        cx = region.get('x', 0) + region.get('w', 0) / 2
        cy = region.get('y', 0) + region.get('h', 0) / 2
        face_center = (cx / w_frame, cy / h_frame)
        self.position_history.append(face_center)

        movement_ok = False
        if len(self.position_history) > 1:
            p1, p2 = self.position_history[-1], self.position_history[-2]
            movement = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
            if movement > self.MOVEMENT_THRESHOLD:
                movement_ok = True

        return model_ok and movement_ok

    async def _ai_processing_loop(self):
        """核心AI处理循环，包含新的三阶段状态机。"""
        while self.is_running:
            # ... (获取帧的代码保持不变) ...
            frame_to_process = None
            async with self.lock:
                if self.latest_frame is None: await asyncio.sleep(0.02); continue
                frame_to_process = self.latest_frame.copy()
            display_frame = frame_to_process.copy()

            try:
                # 检查是否超时，如果成功状态显示过久则重置
                if self.liveness_state == "PASSED" and time.time() - self.verification_timestamp > self.SUCCESS_DISPLAY_DURATION:
                    logger.info(f"成功状态展示超时，重置系统。")
                    self.reset_state()
                    async with self.lock: self.latest_result.clear()

                detected_faces = await asyncio.to_thread(
                    DeepFace.extract_faces,
                    img_path=frame_to_process, detector_backend=DETECTOR_BACKEND, enforce_detection=False
                )

                if detected_faces:
                    main_face = detected_faces[0]
                    region = main_face['facial_area']

                    # --- 三阶段状态机 ---
                    if self.liveness_state == "CHECKING":
                        # 阶段1: 被动检测 (模型+移动)
                        liveness_data = self.liveness_checker.check(frame_to_process, region)
                        if self._update_passive_check_state(liveness_data, region, frame_to_process.shape):
                            self.passive_check_stable_frames += 1
                        else:
                            self.passive_check_stable_frames = 0  # 任何一次失败都重置计数

                        logger.info(
                            f"Passive Check Stability: {self.passive_check_stable_frames}/{self.PASSIVE_STABILITY_REQUIREMENT}")

                        if self.passive_check_stable_frames >= self.PASSIVE_STABILITY_REQUIREMENT:
                            logger.info("被动检测稳定，进入主动检测阶段。")
                            self.liveness_state = "ACTION_REQUIRED"

                    elif self.liveness_state == "ACTION_REQUIRED":
                        # 阶段2: 主动检测 (张嘴)
                        mouth_ratio = self.mouth_detector.check_mouth_open(frame_to_process)
                        if mouth_ratio is not None:
                            logger.info(f"Mouth Open Ratio: {mouth_ratio:.4f} (Threshold: {self.MOUTH_OPEN_THRESHOLD})")
                            if mouth_ratio > self.MOUTH_OPEN_THRESHOLD:
                                logger.info("✅ 主动检测通过 (嘴巴张开)!")
                                face_crop = main_face['face']
                                face_data = await self.encoder.extract_vector(face_crop)
                                if face_data:
                                    logger.info("特征向量提取成功！验证完成。")
                                    self.liveness_state = "PASSED"
                                    self.vector_extracted = True
                                    self.verification_timestamp = time.time()
                                    async with self.lock:
                                        self.latest_result = face_data
                                        self.latest_result["liveness_passed"] = True
                                else:
                                    logger.warning("嘴部检测通过，但特征提取失败，重置状态。")
                                    self.reset_state()

                    # 无论哪个状态，都绘制可视化框
                    self._draw_visualization(display_frame, region)

                else:
                    # 如果未检测到人脸，重置所有状态
                    if self.liveness_state != "CHECKING" or self.latest_result:
                        logger.info("人脸从画面消失，重置状态。")
                        self.reset_state()
                        async with self.lock: self.latest_result.clear()
                    cv2.putText(display_frame, "No Face Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255),
                                2)

                # ... (更新FPS和processed_frame的代码保持不变) ...
                async with self.lock:
                    self.processed_frame = display_frame

            except Exception as e:
                logger.error(f"AI处理循环中发生错误: {e}", exc_info=True)
                self.reset_state()

            await asyncio.sleep(0.033)

    def _draw_visualization(self, frame: np.ndarray, region: dict):
        """根据当前状态绘制不同的提示信息和框。"""
        x, y, w, h = region['x'], region['y'], region['w'], region['h']

        if self.liveness_state == "CHECKING":
            color = (0, 0, 255)  # 红色
            text = "Checking Liveness..."
            progress = self.passive_check_stable_frames / self.PASSIVE_STABILITY_REQUIREMENT
            cv2.rectangle(frame, (x, y + h + 5), (int(x + w * progress), y + h + 15), (0, 255, 255), -1)

        elif self.liveness_state == "ACTION_REQUIRED":
            color = (0, 165, 255)  # 橙色
            text = "Please Open Your Mouth"

        elif self.liveness_state == "PASSED":
            color = (0, 255, 0)  # 绿色
            text = "Verification Ready"

        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    async def get_video_stream(self):
        """获取视频流生成器"""
        fps_start_time = time.time()
        fps_frame_count = 0
        try:
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
        except GeneratorExit:
            # 当客户端断开连接时会触发这个异常
            logger.info("视频流客户端断开连接")
        except Exception as e:
            logger.error(f"视频流发生错误: {e}")
        finally:
            # 确保在流结束时停止分析
            logger.info("正在清理视频流资源...")
            await self.stop_analysis()
            logger.info("视频流资源清理完成")

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
        await facial_service.start_analysis()
        logger.info("人脸识别服务初始化完成")
    except Exception as e:
        logger.error(f"初始化人脸识别服务时发生错误: {e}")
        raise

@router.on_event("shutdown")
async def shutdown_event():
    """服务关闭时的清理"""
    try:
        logger.info("正在关闭人脸识别服务...")
        await facial_service.stop_analysis()
        logger.info("人脸识别服务已关闭")
    except Exception as e:
        logger.error(f"关闭人脸识别服务时发生错误: {e}")

@router.get("/video_feed")
async def video_feed():
    try:
        await facial_service.start_analysis()
        return StreamingResponse(
            facial_service.get_video_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except Exception as e:
        await facial_service.stop_analysis()
        raise

@router.get("/video_feed_cors")
async def video_feed_cors():
    """支持CORS的视频流接口，用于前端跨域访问"""
    try:
        await facial_service.start_analysis()
        response = StreamingResponse(
            facial_service.get_video_stream(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
        # 添加CORS头
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        return response
    except Exception as e:
        await facial_service.stop_analysis()
        raise

@router.get("/get_latest_vector")
async def get_latest_vector():
    try:
        logger.info("接收到人脸采集任务")

        # 启动分析
        await facial_service.start_analysis()
        
        # 等待最多10秒获取结果
        start_time = time.time()
        while time.time() - start_time < 10:
            result = await facial_service.get_latest_face_info()
            if result and result.get("vector_str"):
                await facial_service.stop_analysis()
                logger.info("人脸采集成功")
                return JSONResponse(content={
                    "status": "success",
                    "model": MODEL_NAME,
                    "data": {
                        "vector": result["vector_str"],
                        "face_location": result["region"]
                    }
                })
            await asyncio.sleep(0.1)
        
        # 超时处理
        await facial_service.stop_analysis()
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "未能在指定时间内获取到有效的人脸特征向量。"}
        )
    except Exception as e:
        await facial_service.stop_analysis()
        raise