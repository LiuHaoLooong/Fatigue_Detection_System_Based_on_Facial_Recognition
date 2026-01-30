# 疲劳检测系统

一个基于MediaPipe Face Mesh的疲劳检测系统，可以检测疲劳状态并发出警报。

## 项目结构

```
FinalProject/
├── config.py              # 配置模块 - 所有可调整的参数
├── utils.py               # 工具函数模块 - 计算函数
├── face_detector.py       # 面部检测模块 - MediaPipe Face Mesh封装
├── fatigue_detector.py    # 疲劳检测模块 - 眨眼、打哈欠、头部姿态检测
├── fatigue_level.py      # 疲劳等级模块 - 综合计算疲劳等级
├── alarm.py              # 警报模块 - 声音警报管理
├── ui.py                 # UI绘制模块 - 绘制所有UI元素
├── web_server.py         # Web服务器模块 - 提供Web界面
├── main.py               # 主程序入口 - 整合所有模块
├── requirements.txt        # 依赖包列表
├── templates/            # HTML模板目录
│   └── index.html       # Web界面主页
├── static/              # 静态文件目录
│   ├── css/
│   │   └── style.css    # CSS样式文件
│   └── js/
│       └── app.js       # JavaScript客户端代码
└── README.md             # 项目说明文档
```

## 功能特性

- **眨眼检测**：使用眼睛纵横比（EAR）算法检测眨眼频率和闭眼时长
- **打哈欠检测**：使用嘴部纵横比（MAR）算法检测打哈欠
- **头部姿态检测**：检测头部倾斜角度，判断是否低头
- **疲劳等级评估**：综合多个指标计算疲劳等级和评分
- **声音警报**：检测到疲劳状态时发出蜂鸣声
- **实时UI显示**：显示疲劳状态、疲劳等级、眨眼次数、打哈欠次数等详细信息
- **Web界面**：提供现代化的Web界面，支持远程访问和实时监控

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 桌面界面模式

```bash
python main.py
```

按 `q` 键退出程序

### Web界面模式

```bash
python main.py --web
```

或者指定服务器地址和端口：

```bash
python main.py --web --host 0.0.0.0 --port 5000
```

然后在浏览器中打开：`http://localhost:5000`

按 `q` 键退出程序

### 退出程序

按 `q` 键退出程序

## 参数配置

所有可调整的参数都在 `config.py` 文件中：

```python
# 摄像头设置
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_INDEX = 0

# 眼睛纵横比阈值（越小越敏感）
EAR_THRESHOLD = 0.25

# 连续闭眼帧数阈值（约2秒）
EYE_AR_CONSEC_FRAMES = 60

# 嘴部张开阈值（越小越敏感）
MOUTH_AR_THRESHOLD = 0.65

# 连续打哈欠帧数阈值（约2秒）
YAWN_CONSEC_FRAMES = 60

# 低头角度阈值（度）
HEAD_TILT_THRESHOLD = 30

# 警报冷却时间（秒）
ALARM_COOLDOWN = 2.0
```

## 模块说明

### config.py

配置模块，包含所有可调整的参数：

- 摄像头设置
- 检测阈值
- 颜色定义
- UI设置

### utils.py

工具函数模块，包含各种计算函数：

- `calculate_ear()`: 计算眼睛纵横比
- `calculate_mar()`: 计算嘴部纵横比
- `calculate_head_tilt()`: 计算头部倾斜角度
- `get_eye_landmarks()`: 获取眼睛特征点
- `get_mouth_landmarks()`: 获取嘴部特征点

### face_detector.py

面部检测模块，封装MediaPipe Face Mesh：

- `FaceDetector`: 面部检测器类
- `process()`: 处理图像，检测面部特征点
- `draw_face_mesh()`: 绘制面部特征点网格
- `get_landmarks_array()`: 转换特征点为numpy数组

### fatigue_detector.py

疲劳检测模块，检测各种疲劳指标：

- `FatigueDetector`: 疲劳检测器类
- `detect()`: 检测疲劳状态
- `_detect_blink()`: 检测眨眼
- `_detect_yawn()`: 检测打哈欠
- `_detect_head_pose()`: 检测头部姿态
- `get_blink_rate()`: 获取眨眼频率
- `get_eye_closed_duration()`: 获取闭眼时长

### fatigue_level.py

疲劳等级模块，综合计算疲劳等级：

- `FatigueLevel`: 疲劳等级枚举（正常、轻度、中度、重度）
- `FatigueLevelCalculator`: 疲劳等级计算器类
- `calculate()`: 计算疲劳等级和评分
- `_calculate_blink_score()`: 计算眨眼频率得分
- `_calculate_yawn_score()`: 计算打哈欠得分
- `_calculate_eye_closed_score()`: 计算闭眼时长得分
- `_calculate_head_pose_score()`: 计算头部姿态得分
- `get_average_score()`: 获取平均得分
- `get_trend()`: 获取疲劳趋势

### alarm.py

警报模块，处理疲劳状态的声音警报：

- `AlarmManager`: 警报管理器类
- `check_and_trigger()`: 检查是否需要发出警报
- `enable()` / `disable()`: 启用/禁用警报
- `set_cooldown()`: 设置警报冷却时间

### ui.py

UI绘制模块，负责绘制所有UI元素：

- `UIDrawer`: UI绘制器类
- `draw_eye_region()`: 绘制眼睛区域
- `draw_mouth_region()`: 绘制嘴部区域
- `draw_status_panel()`: 绘制状态面板
- `draw_fatigue_level()`: 绘制疲劳等级
- `draw_all()`: 绘制所有UI元素

### web_server.py

Web服务器模块，提供Web界面：

- `WebServer`: Web服务器类
- `update_frame()`: 更新视频帧
- `update_fatigue_data()`: 更新疲劳数据
- `start()` / `stop()`: 启动/停止服务器

### main.py

主程序入口，整合所有模块：

- `FatigueDetectionSystem`: 疲劳检测系统主类
- `initialize_camera()`: 初始化摄像头
- `process_frame()`: 处理单帧图像
- `run()`: 运行疲劳检测系统
- `cleanup()`: 清理资源

## 应用场景

1. **驾驶疲劳预警**：提醒驾驶员休息
2. **长时间工作提醒**：防止过度疲劳
3. **健康监测**：记录眨眼频率和打哈欠次数

## 技术特点

- **高精度**：使用MediaPipe Face Mesh进行468个面部特征点检测
- **实时性**：30FPS流畅运行
- **稳定性**：使用历史数据平滑处理
- **模块化**：清晰的代码结构，易于维护和扩展
- **可配置**：所有参数都可以在config.py中调整

## 注意事项

1. 确保摄像头正常工作
2. 光线充足，面部清晰可见
3. 根据实际使用情况调整检测阈值
4. 警报声音仅在Windows系统下有效（使用winsound）

## 许可证

本项目仅供学习和研究使用。
