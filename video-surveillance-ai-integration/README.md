# 视频监控危险行为检测系统

本系统集成了视频分析、音频监控、AI大模型与Web前端，支持危险行为（如摔倒、打架、区域入侵、教室喧哗等）自动检测与智能告警。

---

## 主要功能

- **视频行为检测**：摔倒检测、打架检测、危险区域入侵、区域停留等
- **音频监控**：环境噪音、喧哗、异常声学事件检测，分贝统计
- **AI模型集成**：支持YOLO等视觉大模型，支持自定义AI推理
- **Web前端**：实时视频流、告警详情、分贝曲线、历史查询
- **多模态联动**：行为与声学检测结果联动展示
- **告警推送与处理**：支持MySQL数据库存储、告警处理、图片归档

---

## 安装与运行

### 依赖环境

- Python 3.8+
- OpenCV
- Flask
- sounddevice, librosa, tensorflow, tensorflow_hub
- MySQL（用于告警存储，或可选用SQLite）
- 详见 `requirements.txt`

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动系统

```bash
python src/all_in_one_system.py --web_interface --enable_audio_monitor --output system_output
```

常用参数说明：
- `--web_interface` 启用Web前端
- `--enable_audio_monitor` 启用音频监控
- `--output` 输出目录
- `--feature_threshold` 特征点阈值（影响摔倒灵敏度）
- `--dwell_time_threshold` 区域停留告警时间阈值

### 配置与自定义

- 配置参数可通过命令行传递，或修改 `src/danger_recognizer.py` 里的默认参数
- AI模型可替换为自定义YOLO权重或其他模型
- 前端模板在 `templates/`，静态资源在 `static/`

---

## 目录结构

```
src/
  all_in_one_system.py      # 主入口，集成所有功能
  audio_monitor.py          # 音频监控与分贝统计
  danger_recognizer.py      # 危险行为检测核心
  models/                   # 告警、AI、数据库等模型
  templates/                # Web前端HTML模板
  static/                   # 前端静态资源
requirements.txt            # 依赖列表
README.md                   # 本文档
```

