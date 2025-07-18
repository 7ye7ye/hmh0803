# Web界面配置指南

## 概述

视频监控系统现在支持通过Web界面进行实时配置，无需在命令行中输入参数。用户可以通过浏览器界面设置停留时间阈值和框选警戒区域。

## 启动系统

### 方法1: 使用批处理文件（推荐）
```bash
run_web_system.bat
```

### 方法2: 命令行启动
```bash
python src/all_in_one_system.py --web_interface --source 0 --width 640 --height 480 --max_fps 30
```

## 访问Web界面

启动系统后，在浏览器中访问：
```
http://localhost:5000
```

## 功能说明

### 1. 停留时间阈值设置

在右侧配置面板中：
- 在"停留时间阈值（秒）"输入框中输入数值（0.1-60.0秒）
- 点击"设置阈值"按钮
- 系统会立即更新危险区域停留检测的时间阈值

**说明：** 当人员在警戒区域内停留超过设定时间时，系统会触发告警。

### 2. 警戒区域框选

#### 框选步骤：
1. 点击"开始框选"按钮
2. 鼠标光标变为十字形
3. 在视频画面上按住鼠标左键并拖拽，绘制矩形区域
4. 释放鼠标左键完成框选
5. 系统会自动设置该区域为警戒区域

#### 重置区域：
- 点击"重置区域"按钮可以清除当前设置的警戒区域

### 3. 实时监控

- **视频流：** 实时显示摄像头画面，警戒区域用蓝色框显示
- **系统状态：** 显示当前帧率、处理帧数、运行时间等
- **告警列表：** 实时显示检测到的告警信息
- **告警统计：** 显示总告警数、已处理数、未处理数

## 技术特性

### 前端功能
- **响应式设计：** 适配不同屏幕尺寸
- **实时更新：** 配置更改立即生效
- **用户友好：** 直观的鼠标框选界面
- **状态反馈：** 操作成功/失败提示

### 后端API
- **RESTful接口：** 标准的HTTP API设计
- **实时配置：** 支持运行时动态更新参数
- **错误处理：** 完善的异常处理和错误提示
- **线程安全：** 多线程环境下的数据安全

## API接口

### 设置停留时间阈值
```
POST /config/dwell_time_threshold
Content-Type: application/json

{
    "threshold": 2.5
}
```

### 设置警戒区域
```
POST /config/alert_region
Content-Type: application/json

{
    "region": [
        [100, 100],
        [300, 100],
        [300, 300],
        [100, 300]
    ]
}
```

### 重置警戒区域
```
POST /config/reset_alert_region
```

## 测试功能

运行测试脚本验证功能：
```bash
python test_web_config.py
```

## 注意事项

1. **浏览器兼容性：** 建议使用Chrome、Firefox、Edge等现代浏览器
2. **网络连接：** 确保本地网络连接正常
3. **摄像头权限：** 首次访问时浏览器可能会请求摄像头权限
4. **系统要求：** 需要Python 3.7+和相关依赖包

## 故障排除

### 常见问题

1. **无法访问Web界面**
   - 检查系统是否正常启动
   - 确认端口5000未被占用
   - 检查防火墙设置

2. **框选功能不工作**
   - 确保点击了"开始框选"按钮
   - 检查浏览器是否支持鼠标事件
   - 刷新页面重试

3. **配置不生效**
   - 检查浏览器控制台是否有错误信息
   - 确认网络连接正常
   - 重启系统重试

### 日志查看

系统运行日志保存在：
```
all_in_one_system.log
```

## 更新日志

### v1.0.0
- 新增Web界面配置功能
- 支持鼠标框选警戒区域
- 支持实时设置停留时间阈值
- 新增配置面板和交互界面
- 完善错误处理和用户反馈 