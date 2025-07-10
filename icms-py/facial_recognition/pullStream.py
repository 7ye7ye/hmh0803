import cv2
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse,JSONResponse
from deepface import DeepFace

from typing import Optional, List

import numpy as np

# --- 配置 ---
# 视频流源地址
# 注意：请确保这个地址在你运行代码时是可访问的。
# 如果该流不稳定或失效，你需要替换成一个有效的视频流地址。
# 例如一个本地摄像头：0，或者一个RTSP流： "rtsp://..."
VIDEO_STREAM_URL = "rtmp://120.46.210.148:1935/live/livestream"

# DeepFace 模型配置
MODEL_NAME = "Facenet512"
DETECTOR_BACKEND = 'opencv'

# --- 全局状态管理 ---
# 使用一个简单的字典来存储最新的识别结果
# 在生产环境中，推荐使用更健壮的状态管理方式，如 Redis
latest_recognition_data = {
    "vector": None,
    "location": None
}

# --- FastAPI 应用实例 ---
app = FastAPI()

def process_frame_for_ai(frame: np.ndarray):
    """
       对单帧图像进行AI处理的函数。
       此函数现在使用 DeepFace 进行人脸检测和向量提取。

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

    global latest_recognition_data

    try:
        # 1. 使用 DeepFace.analyze 快速检测人脸位置
        # 'actions=['age']' 是一个触发检测的轻量级动作
        face_objects = DeepFace.analyze(
            img_path=frame,
            actions=['age'],
            enforce_detection=False,
            detector_backend=DETECTOR_BACKEND
        )

        # 检查是否检测到人脸 (DeepFace返回一个列表，每个元素代表一张脸)
        if face_objects and isinstance(face_objects, list) and len(face_objects) > 0:
            # 只处理检测到的第一张人脸
            face_info = face_objects[0]
            region = face_info['region']  # {'x': int, 'y': int, 'w': int, 'h': int}

            # 2. 截取人脸区域，以提高向量提取的效率
            face_img = frame[region['y']:region['y'] + region['h'], region['x']:region['x'] + region['w']]

            # 确保截取的人脸图像不为空
            if face_img.size > 0:
                # 3. 使用 DeepFace.represent 提取特征向量
                embedding_objs = DeepFace.represent(
                    img_path=face_img,
                    model_name=MODEL_NAME,
                    enforce_detection=False,  # 因为已截取人脸，此处设为False
                    detector_backend=DETECTOR_BACKEND
                )

                if embedding_objs and len(embedding_objs) > 0:
                    # 4. 提取向量并更新全局状态
                    face_vector = embedding_objs[0]['embedding']
                    latest_recognition_data["vector"] = face_vector
                    latest_recognition_data["location"] = region
                    print(f"成功更新人脸向量，维度: {len(face_vector)}")

            # 5. 在原始帧上绘制矩形框和提示文字
            cv2.rectangle(frame, (region['x'], region['y']), (region['x'] + region['w'], region['y'] + region['h']),
                          (0, 255, 0), 2)
            cv2.putText(frame, "Face Vector Extracted", (region['x'], region['y'] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    except Exception as e:
        # 如果处理过程中发生任何错误，打印出来但保持程序运行
        print(f"AI处理时发生错误: {e}")

        # 无论是否检测到人脸，都返回（可能被修改过的）帧
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
        frame_counter = 0  # 增加一个帧计数器用于性能优化
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

            frame_counter += 1
            # --- 在这里进行AI处理 ---
            # 性能优化：每隔3帧才进行一次AI处理
            if frame_counter % 3 == 0:
                # --- 在这里进行AI处理 ---
                processed_frame = process_frame_for_ai(frame)
            else:
                # 其他帧直接返回，不进行AI处理
                processed_frame = frame

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
    return {
        "message": "欢迎使用视频处理API", "stream_url": "/video_feed",
        "stream_url":"/video_feed",
        "vector_api":"/get_lastest_vector"
    }


@app.get("/video_feed")
async def video_feed():
    """
    视频流传输接口。
    它会返回一个StreamingResponse，内容由video_stream_generator生成。
    """
    # 返回一个流式响应
    # media_type 中的 "multipart/x-mixed-replace" 是实现MJPEG流的关键
    # "boundary=frame" 定义了帧之间的边界
    return StreamingResponse(video_stream_generator(),
                             media_type="multipart/x-mixed-replace; boundary=frame")

# --- 新增的 API 接口 ---
@app.get("/get_latest_vector")
async def get_latest_vector():
    """
    提供一个API端点，用于获取最近一次成功提取到的人脸特征向量。
    """
    if latest_recognition_data["vector"]:
        # 如果全局变量中有向量数据，则构造一个成功的JSON响应
        response_data = {
            "status": "success",
            "model": MODEL_NAME,
            "data": {
                "vector": latest_recognition_data["vector"],
                "face_location": latest_recognition_data["location"]
            }
        }
        return JSONResponse(content=response_data)
    else:
        # 如果还没有提取到向量，则返回一个表示未找到的JSON响应
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": "No face vector has been extracted from the stream yet."
            }
        )