import cv2
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse

# --- 配置 ---
# 视频流源地址
# 注意：请确保这个地址在你运行代码时是可访问的。
# 如果该流不稳定或失效，你需要替换成一个有效的视频流地址。
# 例如一个本地摄像头：0，或者一个RTSP流： "rtsp://..."
VIDEO_STREAM_URL = "rtmp://120.46.210.148:1935/live/livestream"

# --- FastAPI 应用实例 ---
app = FastAPI()

# 定义允许的来源列表
# 这里的 "http://localhost:8080" 是您的 Vue 前端应用的地址
# 如果前端部署在其他域名或端口，需要相应修改
# 生产环境中，强烈建议只列出您的前端域名，而不是 "*"
origins = [
    "http://localhost",       # 允许 localhost
    "http://localhost:8085",  # 允许 Vue 开发服务器
    # "http://your-frontend-domain.com", # 如果部署到其他域名，也需要添加
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,                  # 允许的来源列表
    allow_credentials=True,                 # 允许发送 cookie
    allow_methods=["*"],                    # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE 等)
    allow_headers=["*"],                    # 允许所有 HTTP 请求头
)


def process_frame_for_ai(frame):
    """
    对单帧图像进行AI处理的函数。
    这里是一个演示，我们简单地在图像上画一个矩形和添加一些文字。
    在实际应用中，您应该在这里集成您的AI模型（例如目标检测、人脸识别等）。

    :param frame: 从视频流中捕获的一帧图像 (NumPy array)
    :return: 处理后的图像 (NumPy array)
    """
    # 获取图像的高度和宽度
    h, w, _ = frame.shape

    # 在图像中心画一个绿色的矩形框
    # 参数: (图像, 左上角坐标, 右下角坐标, 颜色 BGR, 线条宽度)
    cv2.rectangle(frame, (w // 4, h // 4), (w * 3 // 4, h * 3 // 4), (0, 255, 0), 2)

    # 在图像上添加文字
    # 参数: (图像, 文字内容, 起始坐标, 字体, 字体大小, 颜色 BGR, 字体粗细)
    cv2.putText(frame, "AI Processing...", (w // 4, h // 4 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    return frame


async def video_stream_generator():
    """
    视频流生成器，它会持续从源地址读取帧，处理后以JPEG格式yield出去。
    """
    # 使用OpenCV打开视频流
    cap = cv2.VideoCapture(VIDEO_STREAM_URL)

    # 检查视频流是否成功打开
    if not cap.isOpened():
        print(f"错误: 无法打开视频流 {VIDEO_STREAM_URL}")
        # 如果无法打开，可以yield一张错误提示图片
        # (此处为了简化，我们直接返回)
        return

    print("视频流已成功打开，开始逐帧处理...")
    try:
        while True:
            # 读取一帧
            ret, frame = cap.read()

            # 如果ret为False，说明读取失败或视频流已结束
            if not ret:
                print("无法读取视频帧，可能视频流已结束或中断。")
                # 等待一小段时间后尝试重连
                await asyncio.sleep(2)
                cap.release()  # 释放旧的捕获对象
                cap = cv2.VideoCapture(VIDEO_STREAM_URL)  # 尝试重新连接
                if not cap.isOpened():
                    print("重连失败，终止推流。")
                    break
                continue

            # --- 在这里进行AI处理 ---
            processed_frame = process_frame_for_ai(frame)

            # 将处理后的帧编码为JPEG格式
            # imencode返回一个元组 (retval, buffer)，我们取第二个元素
            (flag, encodedImage) = cv2.imencode(".jpg", processed_frame)

            # 如果编码失败，跳过这一帧
            if not flag:
                continue

            # 将JPEG数据转换为字节流，并按照MJPEG格式进行封装
            # MJPEG格式要求在每帧数据前加上特定的头部
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')

            # 稍微等待，避免CPU占用过高，也给其他异步任务执行机会
            await asyncio.sleep(0.01)

    finally:
        # 确保在结束时释放资源
        print("释放视频捕获资源。")
        cap.release()


@app.get("/")
def read_root():
    return {"message": "欢迎使用视频处理API", "stream_url": "/video_feed"}


@app.get("/ai/start_facial_recognition/video_feed")
async def video_feed():
    """
    视频流传输接口。
    它会返回一个StreamingResponse，内容由video_stream_generator生成。
    """
    # 返回一个流式响应
    # media_type 中的 "multipart/x-mixed-replace" 是实现MJPEG流的关键
    # "boundary=frame" 定义了帧之间的边界
    return "abc"