# 开发者指南

本指南帮助开发者理解视频监控危险行为检测系统的架构、模块、调试方法及二次开发方式。

## 目录
- [环境设置](#环境设置)
- [系统架构与模块](#系统架构与模块)
- [开发工作流](#开发工作流)
- [调试与排查](#调试与排查)
- [二次开发与扩展](#二次开发与扩展)

---

## 环境设置

- 推荐使用 Python 3.8+
- 建议使用虚拟环境（venv）
- 依赖见 `requirements.txt`
- 数据库可用 MySQL 或 SQLite

---

## 系统架构与模块

- `all_in_one_system.py`：主入口，集成视频、音频、AI、Web等所有功能
- `audio_monitor.py`：音频采集、分贝统计、声学事件推送
- `danger_recognizer.py`：危险行为检测核心，支持摔倒、打架、区域入侵等
- `models/`：告警、AI推理、数据库等模型
- `templates/`、`static/`：Web前端页面与静态资源

### 主要数据流
1. 视频帧采集 → 特征提取 → 危险行为识别 → 告警生成
2. 音频采集 → 分贝统计/事件检测 → recent_audio_events 队列 → 行为告警联动
3. 告警推送 → Web前端展示/数据库存储

---

## 开发工作流

- 推荐分支开发，合并到主分支前充分测试
- 代码风格遵循PEP8，建议使用black/flake8
- 单元测试建议用pytest
- 主要参数可通过命令行或直接修改源码（如 `danger_recognizer.py`）

---

## 调试与排查

- **分贝显示异常**：检查 `audio_monitor.py` 推送逻辑，确认 recent_audio_events 队列有分贝数据
- **摔倒检测不灵敏**：调低 `feature_threshold`、`fall_motion_threshold`，或直接在 `danger_recognizer.py` 修改默认参数
- **Web前端无数据**：检查 Flask 路由、模板、静态资源是否齐全，关注日志输出
- **数据库相关问题**：检查MySQL配置，或切换为SQLite
- **AI模型推理异常**：确认 ultralytics/yolov8 依赖和权重文件

---

## 二次开发与扩展

- **自定义AI模型**：可替换YOLO权重或集成其他视觉模型
- **扩展新行为类型**：在 `danger_recognizer.py` 中添加新检测逻辑
- **前端自定义**：修改 `templates/` 和 `static/` 下的页面和样式
- **API扩展**：在 `all_in_one_system.py` 增加Web路由或API接口

---

## 参考文档
- [快速开始](QUICK_START.md)
- [API参考](API_REFERENCE.md)
- [模块概览](MODULE_OVERVIEW.md)

如有问题请提交issue或联系开发团队。 