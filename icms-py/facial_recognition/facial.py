import cv2
import asyncio
import logging
import time
from fastapi import FastAPI, APIRouter
from fastapi.responses import StreamingResponse, JSONResponse
from deepface import DeepFace
import numpy as np
from typing import Dict, Any

# --- 1. 日志和配置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

VIDEO_STREAM_URL = "rtmp://120.46.210.148:1935/live/livestream"
MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = 'opencv'


# --- 2. 优化后的全局状态管理 (核心) ---
# 使用一个更结构化的状态字典
class AppState:
    def __init__(self):
        self.latest_frame: np.ndarray | None = None  # 最新的原始视频帧
        self.processed_frame: np.ndarray | None = None  # 最新一帧经过AI处理并绘制了结果的帧
        self.latest_vector: list | None = None  # 最新提取的向量
        self.last_face_location: Dict | None = None  # 最新人脸位置
        self.is_ai_processing: bool = False  # AI是否正在处理中 (关键的锁状态)
        self.lock = asyncio.Lock()  # 异步锁，用于安全地修改状态
        self.stats: Dict[str, Any] = {  # 统计信息
            "total_frames_streamed": 0,
            "ai_tasks_triggered": 0,
            "faces_detected": 0,
            "last_detection_time": None,
            "error_count": 0,
            "fps_report": {
                "start_time": time.time(),
                "frame_count": 0,
                "fps": 0.0
            }
        }


# 创建全局应用状态实例
app_state = AppState()

# --- 3. FastAPI 应用和路由 ---
router = APIRouter(prefix="/ai/facial", tags=["facial"])


# --- 4. 独立的、异步的AI处理后台任务 (核心优化) ---
async def ai_processing_task():
    """
    一个独立的后台协程，循环检查是否有新帧需要处理。
    这使得AI处理不会阻塞视频流的推送。
    """
    logger.info("🤖 AI处理后台任务已启动...")
    while True:
        # 如果AI当前空闲，并且有新的视频帧可以处理
        if not app_state.is_ai_processing and app_state.latest_frame is not None:
            # 1. 加锁并标记AI为“处理中”
            async with app_state.lock:
                app_state.is_ai_processing = True
                # 复制一份帧进行处理，避免后续的视频流修改它
                frame_to_process = app_state.latest_frame.copy()

            app_state.stats["ai_tasks_triggered"] += 1
            logger.info(f"🚀 触发第 {app_state.stats['ai_tasks_triggered']} 次AI处理任务...")

            try:
                # 2. 将同步的、阻塞的DeepFace调用放入一个独立的线程中执行 (至关重要)
                # 这可以防止重量级的AI计算阻塞整个应用的事件循环
                results = await asyncio.to_thread(
                    DeepFace.represent,
                    img_path=frame_to_process,
                    model_name=MODEL_NAME,
                    detector_backend=DETECTOR_BACKEND,
                    enforce_detection=True  # 直接强制检测，未检测到会抛出ValueError
                )

                # 3. 处理成功的结果
                if results and len(results) > 0:
                    face_info = results[0]
                    vector = face_info['embedding']
                    region = face_info['facial_area']  # DeepFace新版使用'facial_area'

                    # 安全地更新全局状态
                    async with app_state.lock:
                        app_state.latest_vector = vector
                        app_state.last_face_location = region
                        app_state.stats["faces_detected"] += 1
                        app_state.stats["last_detection_time"] = time.strftime("%Y-%m-%d %H:%M:%S")

                    logger.info(f"✅ AI处理成功，检测到人脸，向量维度: {len(vector)}")

                    # 4. 在处理帧的副本上绘制结果，用于视频流显示
                    cv2.rectangle(frame_to_process, (region['x'], region['y']),
                                  (region['x'] + region['w'], region['y'] + region['h']), (0, 255, 0), 2)
                    cv2.putText(frame_to_process, "Face Detected", (region['x'], region['y'] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    app_state.processed_frame = frame_to_process

            except ValueError:
                # DeepFace在enforce_detection=True且未检测到人脸时会抛出此异常
                logger.info("⚪ AI处理完成，当前帧未检测到人脸。")
                async with app_state.lock:
                    # 可以选择清空上次的向量，或保留
                    app_state.latest_vector = None
                    app_state.last_face_location = None
                # 当未检测到人脸时，我们可以让processed_frame显示原始图像
                app_state.processed_frame = frame_to_process

            except Exception as e:
                logger.error(f"❌ AI处理任务发生严重错误: {e}")
                app_state.stats["error_count"] += 1

            finally:
                # 5. 无论成功与否，都要释放锁，标记AI为空闲
                async with app_state.lock:
                    app_state.is_ai_processing = False

        # 无论是否处理，都短暂休眠，避免空转消耗CPU
        await asyncio.sleep(0.05)  # 休眠50毫秒


# --- 5. 视频流生成器 (现在变得非常轻量) ---
async def video_stream_generator():
    """
    视频流生成器，现在只负责从视频源读取帧，并推送最新的“已处理帧”。
    """
    cap = cv2.VideoCapture(VIDEO_STREAM_URL)
    if not cap.isOpened():
        logger.error(f"❌ 无法打开视频流: {VIDEO_STREAM_URL}")
        return

    logger.info("✅ 视频流连接成功，开始推流...")

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.warning("⚠️ 视频帧读取失败，尝试重连...")
            cap.release()
            await asyncio.sleep(2)
            cap = cv2.VideoCapture(VIDEO_STREAM_URL)
            if not cap.isOpened():
                logger.error("❌ 重连失败，终止推流。")
                break
            continue

        # 1. 安全地更新全局的最新原始帧
        async with app_state.lock:
            app_state.latest_frame = frame
            app_state.stats["total_frames_streamed"] += 1

        # 2. 决定要显示的帧 (核心逻辑)
        # 如果有处理过的帧，就用它；否则用原始帧
        display_frame = app_state.processed_frame if app_state.processed_frame is not None else frame

        # 3. 计算并更新FPS
        stats = app_state.stats["fps_report"]
        stats["frame_count"] += 1
        elapsed_time = time.time() - stats["start_time"]
        if elapsed_time >= 1.0:  # 每秒更新一次FPS
            stats["fps"] = stats["frame_count"] / elapsed_time
            # logger.info(f"Streaming FPS: {stats['fps']:.1f}")
            stats["start_time"] = time.time()
            stats["frame_count"] = 0

        # 在要显示的帧上绘制FPS信息
        cv2.putText(display_frame, f"FPS: {stats['fps']:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255),
                    2)

        # 4. 编码并推送
        (flag, encodedImage) = cv2.imencode(".jpg", display_frame)
        if not flag:
            continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

        # 稍微等待，让出CPU给其他任务，这个值可以根据流的流畅度微调
        await asyncio.sleep(1 / 60)  # 尝试匹配60fps的推送速率


# --- 6. FastAPI应用生命周期事件 ---
@router.on_event("startup")
async def startup_event():
    """应用启动时，创建并启动后台AI任务"""
    logger.info("应用启动，创建AI后台任务...")
    # asyncio.create_task 在后台“点燃”一个协程，让它独立运行
    asyncio.create_task(ai_processing_task())


# --- 7. API 路由定义 (保持不变或微调) ---
@router.get("/")
def read_root():
    return {"message": "人脸识别AI服务", "docs": "/docs"}


@router.get("/video_feed")
async def video_feed():
    return StreamingResponse(video_stream_generator(), media_type="multipart/x-mixed-replace; boundary=frame")


@router.get("/get_latest_vector")
async def get_latest_vector():
    if app_state.latest_vector:
        return JSONResponse(content={
            "status": "success",
            "model": MODEL_NAME,
            "data": {
                "vector": app_state.latest_vector,
                "face_location": app_state.last_face_location
            }
        })
    else:
        return JSONResponse(status_code=404, content={"status": "error", "message": "暂无可用的人脸特征向量。"})


@router.get("/get_stats")
async def get_stats():
    return JSONResponse(content={"status": "success", "data": app_state.stats})


# 主应用引入路由
app = FastAPI(title="实时人脸识别AI服务")
app.include_router(router)