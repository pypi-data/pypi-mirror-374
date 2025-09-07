# rbpop - Elegant PyQt6 Popup Notification Library

A lightweight, modern PyQt6 popup notification library with smooth animations, queue management, and multiple preset styles.

## 🚀 Quick Start

### 1. Installation

```bash
pip install rbpop
```

### 2. Create Popup in One Line

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPMsg

app = QApplication([])  # Must create QApplication first
QPop(QPMsg("Operation successful!"))  # That's it!
```

## 🎯 Pre-built Popup Components

### QPMsg - Basic Message Popup
Simple message notification with default blue theme

```python
from rbpop import QPop, QPMsg

# Basic usage
QPop(QPMsg("Task completed"))

# Full parameters
QPop(QPMsg("message content", title="Title", duration=3000))
```

### Preset Type Popups

| Type | Color | Use Case |
|------|-------|----------|
| `QPInfo` | 🟢 Green | Success messages |
| `QPWarn` | 🟡 Yellow | Warning alerts |
| `QPError` | 🔴 Red | Error notifications |

```python
from rbpop import QPop, QPInfo, QPWarn, QPError

# Success notification
QPop(QPInfo("Data saved successfully!"))

# Warning alert
QPop(QPWarn("Network connection unstable"))

# Error notification
QPop(QPError("Save failed, please retry"))
```

## 🎨 Custom Popups

### Inherit QPMsg for Custom Popups

Create custom popups with specific styles and functionality by inheriting `QPMsg`:

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPMsg

class MySuccessMsg(QPMsg):
    def __init__(self, msg):
        super().__init__(msg, title="✅ Success", duration=2500)
        self.setStyleSheet("""
            background-color: #2ecc71;
            color: white;
            border-radius: 8px;
            font-weight: bold;
        """)

# Use custom popup
app = QApplication([])
QPop(MySuccessMsg("File upload completed!"))
```

### Add Custom Components

Add buttons, input fields, and other interactive elements:

```python
from PyQt6.QtWidgets import QPushButton, QHBoxLayout
from rbpop import QPop, QPMsg

class ConfirmMsg(QPMsg):
    def __init__(self, msg, on_confirm=None):
        super().__init__(msg, title="Confirm Action", duration=0)  # 0 means don't auto-close
        self.on_confirm = on_confirm
        
        # Add confirm button
        self.btn_confirm = QPushButton("Confirm")
        self.btn_confirm.clicked.connect(self.confirm)
        self.layout().addWidget(self.btn_confirm)
    
    def confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.close()

# Use confirmation popup
app = QApplication([])
def handle_confirm():
    print("User confirmed the action")

QPop(ConfirmMsg("Are you sure you want to delete this file?", on_confirm=handle_confirm))
```

## 🎯 Real-world Usage Scenarios

### Scenario 1: User Action Feedback

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPInfo, QPError

app = QApplication([])

def save_data():
    try:
        # Save logic
        save_to_database()
        QPop(QPInfo("Data saved successfully!"))
    except Exception as e:
        QPop(QPError(f"Save failed: {str(e)}"))
```

### Scenario 2: Batch Processing Progress

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPInfo

app = QApplication([])

# Batch processing notifications (auto-queued)
for i in range(1, 6):
    QPop(QPInfo(f"Processing progress: {i}/5", duration=1000))
```

### Scenario 3: Custom Theme Popups

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPMsg

class DarkMsg(QPMsg):
    def __init__(self, text):
        super().__init__(text, title="Dark Mode")
        self.setStyleSheet("""
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 6px;
        """)

app = QApplication([])
QPop(DarkMsg("Switched to dark mode"))
```

## 📋 Complete API Reference

### QPMsg Parameters

```python
QPMsg(message, title=None, duration=4000, **kwargs)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | str | Required | Message content |
| `title` | str | None | Window title |
| `duration` | int | 4000 | Display duration in ms (0 = don't auto-close) |
| `close` | bool | False | Show close button |
| `slide_in` | bool | True | Enable slide-in animation |
| `slide_duration` | int | 800 | Animation duration in ms |

### Preset Type Shortcuts

```python
QPInfo(message, title=None, duration=4000)
QPWarn(message, title=None, duration=4000)
QPError(message, title=None, duration=4000)
```

## 🔧 Advanced Controls

### Batch Window Management

```python
from PyQt6.QtWidgets import QApplication
from rbpop.win import WinManager

app = QApplication([])
manager = WinManager.get_instance()

# Batch control all popups
manager.hide_all()   # Hide all
manager.show_all()   # Show all
manager.clear_all()  # Clear all
```

### Animation Effect Control

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPMsg, QPop

app = QApplication([])

# No animation (instant display)
QPop(QPMsg("No animation message", slide_in=False))

# Slow animation
QPop(QPMsg("Slow slide-in", slide_duration=1500))

# Long display time
QPop(QPMsg("Requires user reading", duration=10000))
```

## 🎮 Run Demo

Interactive demo interface included:

```bash
python ui_demo.py
```

Demo features:
- Real-time creation of various popup types
- Batch testing queue management
- Custom colors and styles
- Animation effect testing

## ⚙️ System Requirements

- Python 3.10+
- PyQt6
- Windows/Linux/macOS

## 📦 Project Structure

```
rbpop/
├── __init__.py          # Main entry (exports QPop and preset popups)
├── win/
│   ├── manager.py       # Window manager (WinManager)
│   └── popped.py        # Popup base class (PopWin)
├── prefab/
│   └── message.py       # Preset popup components (QPMsg/QPInfo/QPWarn/QPError)
└── ui_demo.py          # Demo program
```

## 🎯 Usage Summary

| Use Case | Recommended Approach |
|----------|---------------------|
| Quick message | `QPop(QPMsg("message"))` |
| Success/warning/error | `QPop(QPInfo("success"))` |
| Custom styling | Inherit `QPMsg` to create subclass |
| Full customization | Inherit `PopWin` to build from scratch |

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License - see LICENSE file for details

---

# rbpop - 优雅的PyQt6弹窗管理库

一个轻量级、现代化的PyQt6弹窗通知库，支持平滑动画、队列管理和多种预置样式。

## 🚀 快速上手

### 1. 安装

```bash
pip install rbpop
```

### 2. 一行代码创建弹窗

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPMsg

app = QApplication([])  # 必须先创建QApplication
QPop(QPMsg("操作成功！"))  # 就这么简单！
```

## 🎯 预置弹窗组件

### QPMsg - 基础消息弹窗
最简单的消息提示，默认蓝色主题

```python
from rbpop import QPop, QPMsg

# 基础用法
QPop(QPMsg("操作完成"))

# 完整参数
QPop(QPMsg("消息内容", title="标题", duration=3000))
```

### 预置类型弹窗

| 类型 | 颜色 | 用途 |
|------|------|------|
| `QPInfo` | 🟢 绿色 | 成功信息 |
| `QPWarn` | 🟡 黄色 | 警告提醒 |
| `QPError` | 🔴 红色 | 错误提示 |

```python
from rbpop import QPop, QPInfo, QPWarn, QPError

# 成功提示
QPop(QPInfo("数据保存成功！"))

# 警告提醒  
QPop(QPWarn("网络连接不稳定"))

# 错误提示
QPop(QPError("保存失败，请重试"))
```

## 🎨 自定义弹窗

### 继承QPMsg创建自定义弹窗

通过继承`QPMsg`类，可以快速创建具有特定样式和功能的弹窗：

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPMsg

class MySuccessMsg(QPMsg):
    def __init__(self, msg):
        super().__init__(msg, title="✅ 成功", duration=2500)
        self.setStyleSheet("""
            background-color: #2ecc71;
            color: white;
            border-radius: 8px;
            font-weight: bold;
        """)

# 使用自定义弹窗
app = QApplication([])
QPop(MySuccessMsg("文件上传完成！"))
```

### 添加自定义组件

在继承类中添加按钮、输入框等自定义组件：

```python
from PyQt6.QtWidgets import QPushButton, QHBoxLayout
from rbpop import QPop, QPMsg

class ConfirmMsg(QPMsg):
    def __init__(self, msg, on_confirm=None):
        super().__init__(msg, title="确认操作", duration=0)  # 0表示不自动关闭
        self.on_confirm = on_confirm
        
        # 添加确认按钮
        self.btn_confirm = QPushButton("确认")
        self.btn_confirm.clicked.connect(self.confirm)
        self.layout().addWidget(self.btn_confirm)
    
    def confirm(self):
        if self.on_confirm:
            self.on_confirm()
        self.close()

# 使用确认弹窗
app = QApplication([])
def handle_confirm():
    print("用户确认了操作")

QPop(ConfirmMsg("确定要删除这个文件吗？", on_confirm=handle_confirm))
```

## 🎯 实际应用场景

### 场景1：用户操作反馈

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPInfo, QPError

app = QApplication([])

def save_data():
    try:
        # 保存逻辑
        save_to_database()
        QPop(QPInfo("数据保存成功！"))
    except Exception as e:
        QPop(QPError(f"保存失败：{str(e)}"))
```

### 场景2：批量处理进度

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPInfo

app = QApplication([])

# 批量处理通知（自动排队）
for i in range(1, 6):
    QPop(QPInfo(f"处理进度：{i}/5", duration=1000))
```

### 场景3：自定义主题弹窗

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPop, QPMsg

class DarkMsg(QPMsg):
    def __init__(self, text):
        super().__init__(text, title="夜间模式")
        self.setStyleSheet("""
            background-color: #2c3e50;
            color: #ecf0f1;
            border: 1px solid #34495e;
            border-radius: 6px;
        """)

app = QApplication([])
QPop(DarkMsg("已切换到夜间模式"))
```

## 📋 完整API参数

### QPMsg 参数说明

```python
QPMsg(message, title=None, duration=4000, **kwargs)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `message` | str | 必需 | 消息内容 |
| `title` | str | None | 窗口标题 |
| `duration` | int | 4000 | 显示时长（毫秒，0表示不自动关闭） |
| `close` | bool | False | 是否显示关闭按钮 |
| `slide_in` | bool | True | 是否启用滑入动画 |
| `slide_duration` | int | 800 | 动画时长（毫秒） |

### 预置类型快捷方式

```python
QPInfo(message, title=None, duration=4000)
QPWarn(message, title=None, duration=4000)  
QPError(message, title=None, duration=4000)
```

## 🔧 高级控制

### 批量窗口管理

```python
from PyQt6.QtWidgets import QApplication
from rbpop.win import WinManager

app = QApplication([])
manager = WinManager.get_instance()

# 批量控制所有弹窗
manager.hide_all()   # 隐藏全部
manager.show_all()   # 显示全部  
manager.clear_all()  # 清空全部
```

### 动画效果控制

```python
from PyQt6.QtWidgets import QApplication
from rbpop import QPMsg, QPop

app = QApplication([])

# 无动画（立即显示）
QPop(QPMsg("无动画消息", slide_in=False))

# 慢速动画
QPop(QPMsg("慢速滑入", slide_duration=1500))

# 长时间显示
QPop(QPMsg("需要用户阅读", duration=10000))
```

## 🎮 运行演示

项目内置完整的交互式演示界面：

```bash
python ui_demo.py
```

演示功能：
- 实时创建各种类型弹窗
- 批量测试队列管理  
- 自定义颜色和样式
- 动画效果测试

## ⚙️ 系统要求

- Python 3.10+
- PyQt6
- Windows/Linux/macOS

## 📦 项目结构

```
rbpop/
├── __init__.py          # 主入口（导出QPop和预置弹窗）
├── win/
│   ├── manager.py       # 窗口管理器（WinManager）
│   └── popped.py        # 弹窗基类（PopWin）
├── prefab/
│   └── message.py       # 预置弹窗组件（QPMsg/QPInfo/QPWarn/QPError）
└── ui_demo.py          # 演示程序
```

## 🎯 使用总结

| 需求场景 | 推荐用法 |
|----------|----------|
| 快速消息提示 | `QPop(QPMsg("消息"))` |
| 成功/警告/错误 | `QPop(QPInfo("成功"))` |
| 自定义样式 | 继承`QPMsg`创建子类 |
| 完全自定义 | 继承`PopWin`从零构建 |

## 🤝 参与贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License - 详见LICENSE文件