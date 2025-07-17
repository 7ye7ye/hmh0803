# API 参考文档

本项目提供了视频监控危险行为检测系统的主要组件和API说明，包括Web接口、告警推送、音频事件、AI相关接口等。

## 目录
- [系统主模块](#系统主模块)
- [危险行为识别模块](#危险行为识别模块)
- [音频监控与分贝统计](#音频监控与分贝统计)
- [Web API接口](#web-api接口)
- [常见数据结构](#常见数据结构)

---

## 系统主模块

`src.all_in_one_system.AllInOneSystem`

系统的核心类，集成所有功能模块，提供完整的危险行为检测系统。

### 主要方法

- `start()` 启动系统
- `stop()` 停止系统
- `process_frame(frame)` 处理单帧图像，执行运动分析和危险行为检测
- `generate_report()` 生成系统运行报告

---

## 危险行为识别模块

`src.danger_recognizer.DangerRecognizer`

负责识别视频中的危险行为。

### 主要方法
- `process_frame(frame, features, object_detections=None)`
- `add_alert_region(region, name="警戒区")`

---

## 音频监控与分贝统计

`src/audio_monitor.py`

- 实时采集音频，统计分贝（dBFS+100）
- 检测喧哗、异常声学事件，推送到主系统
- 典型数据结构：
  - `audio_db_stats`: `{ "max_db": 87.3, "min_db": 0, "avg_db": 45.8 }`
  - `audio_labels`: `["Classroom Noise"]` 或异常事件标签

---

## Web API接口

### 1. 获取最新告警
- `GET /alerts`
- 返回：最新10条告警（JSON数组）
- 典型字段：
  - `type`: 告警类型（如 Classroom Noise, Fall Detection 等）
  - `desc`: 告警描述，含分贝统计
  - `audio_db_stats`: 分贝统计（如有）
  - `audio_labels`: 声学标签（如有）
  - `volume_exceeded`: 是否超过音量阈值
  - `volume_threshold`: 音量阈值

### 2. 获取系统统计
- `GET /stats`
- 返回：帧率、告警数、运行时长等

### 3. 处理/取消处理告警
- `POST /alerts/handle`  标记为已处理
- `POST /alerts/unhandle`  取消处理

### 4. 历史告警与分页
- `GET /api/alerts/history?page=1&limit=10`

### 5. 其他接口
- `POST /api/report_stranger_login`  上传陌生人登录图片和告警
- `GET /ai_report`  AI日报页面

---

## 常见数据结构

### 告警对象（Alert）
```json
{
  "id": "...",
  "type": "Classroom Noise",
  "desc": "检测到教室喧哗；检测到最高音量为87.3分贝 (超过音量阈值60分贝)，最小分贝0，平均分贝45.8",
  "audio_db_stats": { "max_db": 87.3, "min_db": 0, "avg_db": 45.8 },
  "audio_labels": ["Classroom Noise"],
  "volume_exceeded": true,
  "volume_threshold": 60,
  ...
}
```

### 音频事件推送
- 由 `audio_monitor.py` 定期推送，主系统 recent_audio_events 队列缓存
- 字段：labels, scores, timestamp, audio_db_stats

---

## 示例：获取告警列表

```bash
curl http://127.0.0.1:5000/alerts
```
返回：
```json
[
  {
    "type": "Classroom Noise",
    "desc": "检测到教室喧哗；检测到最高音量为87.3分贝 (超过音量阈值60分贝)，最小分贝0，平均分贝45.8",
    "audio_db_stats": { "max_db": 87.3, "min_db": 0, "avg_db": 45.8 },
    "audio_labels": ["Classroom Noise"],
    "volume_exceeded": true,
    "volume_threshold": 60
  },
  ...
]
```

---

更多接口和字段详见源码及 Web 路由实现。 