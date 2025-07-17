# 快速开始指南 - Video Surveillance AI Integration

本指南帮助你快速启动本项目，包括环境准备、依赖安装、项目启动及常见问题处理。

## 一、前期准备

### 1. 获取项目代码

```bash
git clone https://github.com/zhizhu505/video-surveillance-ai-integration.git
cd video-surveillance-ai-integration
git checkout zsq  # 切换到主开发分支
```

### 2. 创建并激活虚拟环境

```bash
python -m venv venv
# Windows
venv\Scripts\activate.bat
# Linux/Mac
source venv/bin/activate
```

## 二、安装依赖

```bash
pip install -r requirements.txt
```

如遇 OpenCV、YOLOv8、音频依赖缺失，可分别安装：
```bash
pip install opencv-python opencv-contrib-python
pip install ultralytics
pip install sounddevice tensorflow librosa
```

## 三、启动系统

推荐命令：
```bash
python src/all_in_one_system.py --web_interface --enable_audio_monitor --output system_output
```

常用参数说明：
- `--web_interface` 启用Web前端
- `--enable_audio_monitor` 启用音频监控（分贝统计、喧哗检测）
- `--feature_threshold` 特征点阈值（影响摔倒灵敏度，数值越低越灵敏）
- `--dwell_time_threshold` 区域停留告警时间阈值
- `--output` 输出目录

## 四、访问Web界面

- 本地访问：http://127.0.0.1:5000
- 局域网访问：根据日志显示的实际IP

## 五、系统功能验证

- 视频捕获与处理
- 危险行为检测（摔倒、打架、区域入侵、教室喧哗等）
- 音频监控与分贝统计
- Web前端实时展示与告警详情

## 六、常见问题

- **分贝显示异常？**
  - 分贝采用dBFS+100，正常范围0-100+，如需调整请修改 `audio_monitor.py`。
- **摔倒检测不灵敏？**
  - 可调低 `feature_threshold`、`fall_motion_threshold` 等参数，或直接在 `danger_recognizer.py` 修改默认配置。
- **数据库连接失败？**
  - 检查MySQL配置，或切换为SQLite。
- **摄像头/麦克风无法识别？**
  - 检查设备权限，或指定正确的设备号。
- **Web界面无法访问？**
  - 检查端口、日志输出和 `templates/` 目录下HTML文件是否齐全。

## 七、下一步

- 详细API、开发者指南、AI集成等请参见 docs 目录下相关文档。 