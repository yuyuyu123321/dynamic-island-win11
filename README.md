# Dynamic Island for Windows 11

一个受 macOS Dynamic Island 启发的 Windows 11 桌面灵动岛工具，使用 PyQt6 构建，支持音乐播放、音量控制、系统通知等功能的丝滑动画展示。

## 功能特性

- **媒体播放展示** - 自动检测当前播放的音乐（Spotify、Apple Music、浏览器等），显示专辑封面、歌曲名和艺人
- **音量控制** - 优雅的音量滑块，监听系统音量变化
- **系统通知** - 展示应用通知消息
- **时钟显示** - 简洁的时间显示
- **系统状态** - 电量、WiFi、蓝牙等状态指示
- **丝滑动画** - 展开/收缩动画，自动隐藏
- **拖拽移动** - 支持鼠标拖拽调整位置
- **始终置顶** - 窗口始终显示在最上层
- **自动吸附** - 拖拽后自动吸附到屏幕边缘

## 预览效果

- 默认状态：屏幕顶部居中的小黑胶囊
- 媒体播放：展开显示歌曲信息和控制按钮
- 音量调节：展开显示音量条
- 通知消息：展开显示通知内容
- 空闲状态：自动收缩回小胶囊

## 安装运行

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/dynamic-island-win11.git
cd dynamic-island-win11
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行

```bash
python -m src.main
```

或双击 `run.bat`（Windows）。

## 系统要求

- Windows 10/11
- Python 3.9+
- 推荐使用深色模式以获得最佳视觉效果

## 配置文件

`config.json` 可调整以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `width_collapsed` | 收缩状态宽度 | 120 |
| `height_collapsed` | 收缩状态高度 | 40 |
| `width_expanded` | 展开状态宽度 | 360 |
| `animation_duration` | 动画时长(ms) | 300 |
| `auto_hide_delay` | 自动隐藏延迟(ms) | 3000 |
| `position` | 初始位置 | top-center |

## 项目结构

```
dynamic-island-win11/
├── src/
│   ├── main.py              # 入口文件
│   ├── island.py            # 主窗口
│   ├── animations.py        # 动画系统
│   ├── widgets/             # 各类功能组件
│   │   ├── media_widget.py
│   │   ├── volume_widget.py
│   │   ├── notification_widget.py
│   │   └── clock_widget.py
│   └── utils/               # 工具模块
│       ├── media_listener.py
│       └── system_monitor.py
├── config.json              # 配置文件
├── requirements.txt         # 依赖列表
└── README.md
```

## 技术栈

- **PyQt6** - GUI 框架
- **pycaw** - Windows 音量控制 API
- **winsdk** - Windows Runtime API（媒体控制）
- **psutil** - 系统信息监控
- **pystray** - 系统托盘图标

## 注意事项

- 首次运行可能需要管理员权限以监听系统媒体事件
- 某些应用（如 Spotify）需要在播放音乐时才会显示在灵动岛中
- 自动隐藏后，将鼠标悬停在小胶囊上可快速预览当前状态

## 许可证

MIT License
