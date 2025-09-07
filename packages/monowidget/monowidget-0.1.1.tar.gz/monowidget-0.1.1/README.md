# MonoWidget User Guide

## Project Overview

MonoWidget is a Python tool for creating and managing parameter interfaces. It generates visual interface components through a simple API for defining parameters. It is particularly suitable for rapidly developing configuration interfaces, debugging tools, and parameter debuggers that require user interaction.

## Quick Start

### Installation

MonoWidget is currently a local development library. Simply clone or download the source code to your project.

### Basic Usage Example

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from monowidget import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MonoWidget Example")
        self.setGeometry(100, 100, 600, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Define attribute list
        attrs = [
            MonoAttr("username", "Alice", label="Username"),
            MonoAttr("age", 30, range=(18, 100), label="Age"),
            MonoAttr("active", True, label="Active"),
            MonoAttr("theme", "dark", enum=["light", "dark", "auto"], label="Theme"),
        ]
        
        # Create Mono object
        mono = Mono(attrs)
        
        # Create Inspector and add to layout
        inspector = QMonoInspector(mono)
        main_layout.addWidget(inspector)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

## Core Concepts

### MonoAttr
`MonoAttr` is a parameter definition class used to describe all properties of a single parameter, including name, value, type, range, etc.

### Mono
`Mono` is a data model class that contains multiple `MonoAttr` properties and serves as the data source for `QMonoInspector`.

### QMonoInspector
`QMonoInspector` is the interface renderer responsible for rendering `Mono` objects into visual interfaces.

## Using MonoAttr to Create Inspector

### 1. Import Necessary Modules
```python
from monowidget import *
```

### 2. Define MonoAttr Properties
`MonoAttr` supports multiple parameter types. The system will automatically identify and generate corresponding interface controls based on the `value` type:

#### Supported Type Comparison Table

| Type | Python Value Example | Interface Control |
|------|---------------------|-------------------|
| **String** | `"text"` | Text input box |
| **Integer** | `42` | Number input box |
| **Float** | `3.14` | Float input box |
| **Boolean** | `True` | Checkbox |
| **Enum** | `"option1"` | Dropdown selection |
| **List** | `[1, 2, 3]` | List editor |
| **Dict** | `{"key": "value"}` | Dictionary editor |
| **Function Button** | `lambda: print("hi")` | Button |
| **DateTime** | `datetime.now()` | DateTime picker |
| **Color** | `"#ff0000"` | Color picker |

#### Usage Example
```python
from datetime import datetime

attrs = [
    # Basic types
    MonoAttr("name", "Example", label="Name"),           # String
    MonoAttr("count", 42, label="Count"),                # Integer
    MonoAttr("price", 29.99, label="Price"),             # Float
    MonoAttr("enabled", True, label="Enabled"),          # Boolean
    
    # Range-limited numbers
    MonoAttr("volume", 75, range=(0, 100, 5), label="Volume"),
    
    # Enum type
    MonoAttr("mode", "normal", enum=["easy", "normal", "hard"], label="Mode"),
    
    # Complex types
    MonoAttr("tags", ["python", "qt"], label="Tags"),      # List
    MonoAttr("settings", {"theme": "dark", "font": 14}, label="Settings"),  # Dict
    
    # Function button
    MonoAttr("save_button", lambda: print("Saved"), label="Save Settings"),
    
    # DateTime
    MonoAttr("start_time", datetime.now(), label="Start Time"),
    
    # Color
    MonoAttr("bg_color", "#ffffff", label="Background Color")
]
```

### 3. Create Mono Object
Use the attribute list to create a `Mono` object:
```python
mono = Mono(attrs)
```

### 4. Create and Display Inspector
```python
# Create QMonoInspector instance
inspector = QMonoInspector(mono)

# Add to layout
layout.addWidget(inspector)
```

### 5. Advanced Configuration - Grouping and Titles
You can use `group`, `header`, and `title` parameters to organize the interface layout:

```python
attrs = [
    # Page title
    MonoAttr("app_title", "Configuration Center", title="Application Configuration Center"),
    
    # User info group
    MonoAttr("username", "admin", label="Username", group="User Info", header="👤 User Configuration"),
    MonoAttr("email", "admin@example.com", label="Email", group="User Info"),
    
    # Interface settings group
    MonoAttr("theme", "dark", enum=["light", "dark"], label="Theme", group="Interface Settings", header="🎨 Appearance Settings"),
```

---

# MonoWidget 使用指南

## 项目简介

MonoWidget 是一个用于创建和管理参数界面的Python工具，通过简洁的API定义参数，并自动生成可视化的界面组件。它特别适用于快速开发需要用户交互的配置界面、调试工具和参数调试器等场景。

## 快速开始

### 安装

MonoWidget 目前是一个本地开发库，直接克隆或下载源代码到您的项目中即可使用。

### 基本使用示例

```python
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from monowidget import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MonoWidget 示例")
        self.setGeometry(100, 100, 600, 400)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 定义属性列表
        attrs = [
            MonoAttr("username", "Alice", label="用户名"),
            MonoAttr("age", 30, range=(18, 100), label="年龄"),
            MonoAttr("active", True, label="是否激活"),
            MonoAttr("theme", "dark", enum=["light", "dark", "auto"], label="界面主题"),
        ]
        
        # 创建Mono对象
        mono = Mono(attrs)
        
        # 创建Inspector并添加到布局
        inspector = QMonoInspector(mono)
        main_layout.addWidget(inspector)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
```

## 核心概念

### MonoAttr
`MonoAttr` 是参数定义类，用于描述单个参数的所有属性，包括名称、值、类型、范围等。

### Mono
`Mono` 是数据模型类，包含多个 `MonoAttr` 属性，作为 `QMonoInspector` 的数据源。

### QMonoInspector
`QMonoInspector` 是界面渲染器，负责将 `Mono` 对象渲染为可视化界面。

## 使用 MonoAttr 创建 Inspector

### 1. 导入必要的模块
```python
from monowidget import *
```

### 2. 定义 MonoAttr 属性
`MonoAttr` 支持多种参数类型，系统会根据 `value` 的类型自动识别并生成相应的界面控件：

#### 支持的类型对照表

| 类型 | Python值示例 | 界面控件 |
|------|-------------|----------|
| **字符串** | `"text"` | 文本输入框 |
| **整数** | `42` | 数字输入框 |
| **浮点数** | `3.14` | 浮点输入框 |
| **布尔值** | `True` | 复选框 |
| **枚举** | `"option1"` | 下拉选择框 |
| **列表** | `[1, 2, 3]` | 列表编辑器 |
| **字典** | `{"key": "value"}` | 字典编辑器 |
| **函数按钮** | `lambda: print("hi")` | 按钮 |
| **日期时间** | `datetime.now()` | 日期时间选择器 |
| **颜色** | `"#ff0000"` | 颜色选择器 |

#### 使用示例
```python
from datetime import datetime

attrs = [
    # 基本类型
    MonoAttr("name", "Example", label="名称"),           # 字符串
    MonoAttr("count", 42, label="数量"),                # 整数
    MonoAttr("price", 29.99, label="价格"),             # 浮点数
    MonoAttr("enabled", True, label="启用"),             # 布尔值
    
    # 带范围限制的数值
    MonoAttr("volume", 75, range=(0, 100, 5), label="音量"),
    
    # 枚举类型
    MonoAttr("mode", "normal", enum=["easy", "normal", "hard"], label="模式"),
    
    # 复杂类型
    MonoAttr("tags", ["python", "qt"], label="标签"),      # 列表
    MonoAttr("settings", {"theme": "dark", "font": 14}, label="设置"),  # 字典
    
    # 函数按钮
    MonoAttr("save_button", lambda: print("已保存"), label="保存设置"),
    
    # 日期时间
    MonoAttr("start_time", datetime.now(), label="开始时间"),
    
    # 颜色
    MonoAttr("bg_color", "#ffffff", label="背景颜色")
]
```

### 3. 创建 Mono 对象
使用属性列表创建 `Mono` 对象：
```python
mono = Mono(attrs)
```

### 4. 创建并显示 Inspector
```python
# 创建QMonoInspector实例
inspector = QMonoInspector(mono)

# 添加到布局
layout.addWidget(inspector)
```

### 5. 高级配置 - 分组和标题
您可以使用 `group`、`header` 和 `title` 参数来组织界面布局：

```python
attrs = [
    # 页面标题
    MonoAttr("app_title", "配置中心", title="应用配置中心"),
    
    # 用户信息分组
    MonoAttr("username", "admin", label="用户名", group="用户信息", header="👤 用户配置"),
    MonoAttr("email", "admin@example.com", label="邮箱", group="用户信息"),
    
    # 界面设置分组
    MonoAttr("theme", "dark", enum=["light", "dark"], label="主题", group="界面设置", header="🎨 外观设置"),
]
```

## 数据读写方法

### 方法1：使用字典形式读取所有参数值
```python
# 获取所有参数值（字典形式）
values = inspector.params  # 返回包含所有参数值的字典
print(values)  # 输出: {'username': 'Alice', 'age': 30, ...}

# 设置多个参数值
inspector.params = {
    'username': 'Bob',
    'age': 25
}
```

### 方法2：使用 inspector.vs 访问单个属性
```python
# 读取单个参数值
username = inspector.vs.username
print(f"当前用户名: {username}")

# 修改单个参数值
inspector.vs.username = "Charlie"
inspector.vs.age = 35

# 批量更新多个属性的值
new_values = {
    'username': 'David',
    'age': 40,
    'active': False
}
for key, value in new_values.items():
    setattr(inspector.vs, key, value)
```

### 方法3：监听参数变化事件
```python
# 监听单个参数变化
inspector.paramChanged.connect(lambda name, value: print(f"参数 {name} 已更改为: {value}"))

# 监听所有参数变化
inspector.paramsChanged.connect(lambda params: print(f"所有参数已更新: {params}"))

# 监听特定参数的变化（通过条件判断）
def on_param_changed(name, value):
    if name == "username":
        print(f"用户名已更改为: {value}")
    elif name == "volume":
        print(f"音量设置为: {value}")
        # 这里可以添加实际的处理逻辑
        update_audio_volume(value)

inspector.paramChanged.connect(on_param_changed)
```

## 常见问题

### 1. 如何控制组件的只读状态？
使用 `readonly=True` 参数：
```python
MonoAttr("server_url", "https://api.example.com", readonly=True, label="服务器地址")
```

### 2. 如何添加分隔符和空白间隔？
使用 `separator=True` 和 `space=True` 参数：
```python
attrs = [
    MonoAttr("section1", "第一部分", title="第一部分"),
    MonoAttr("param1", "value1", label="参数1"),
    MonoAttr("param2", "value2", label="参数2", separator=True),  # 添加分隔线
    MonoAttr("section2", "第二部分", title="第二部分"),
    MonoAttr("param3", "value3", label="参数3", space=True),     # 添加上方空白
]
```

### 3. 如何处理参数变化事件？
使用信号槽机制监听参数变化：
```python
# 监听单个参数变化
inspector.paramChanged.connect(lambda name, value: print(f"参数 {name} 已更改为: {value}"))

# 监听所有参数变化
inspector.paramsChanged.connect(lambda params: print(f"所有参数已更新: {params}"))

# 监听特定参数的变化（通过条件判断）
def on_param_changed(name, value):
    if name == "username":
        print(f"用户名已更改为: {value}")
    elif name == "volume":
        print(f"音量设置为: {value}")
        # 这里可以添加实际的处理逻辑
        update_audio_volume(value)

inspector.paramChanged.connect(on_param_changed)
```

## 示例应用说明

项目包含多个示例文件，展示了MonoWidget的各种用法：

- **main.py**: 基础示例，展示如何创建简单的参数界面
- **debug_type_change_value.py**: 调试示例，展示各种数据类型的参数界面
- **inspector/**: Inspector相关模块，包含所有界面组件的实现
- **_utils/**: 工具模块，包含各种辅助类和组件

您可以通过运行 `main.py` 来查看基础示例，或者参考各个模块的源代码了解更详细的实现。