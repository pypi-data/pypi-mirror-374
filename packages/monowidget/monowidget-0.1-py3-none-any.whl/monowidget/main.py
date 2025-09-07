#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MonoWidget - 综合参数调试器

主程序入口，包含完整的MonoAttr系统演示
"""

import sys
import os
import random
import string
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QScrollArea
from PyQt6.QtCore import Qt

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from monowidget import *
from mono.mono_attr import MonoAttr
from inspector.mono_attr_item_factory import QMonoAttrItemFactory
from _utils.ordered_dict import IdOrderedDict


class ListDictTypeTester:
    """测试list和dict类型组件的值返回类型"""
    
    def __init__(self):
        # 创建测试数据
        self._create_test_data()
        
    def _create_test_data(self):
        """创建测试用的数据"""
        # 测试list类型
        self.list_attr_dict = {
            'name': 'test_list',
            'value': ['item1', 'item2', 'item3'],
            'type': list,
            'label': '测试列表',
            'readonly': False
        }
        
        # 测试dict类型
        self.dict_attr_dict = {
            'name': 'test_dict',
            'value': {'key1': 'value1', 'key2': 42, 'key3': True},
            'type': dict,
            'label': '测试字典',
            'readonly': False
        }
        
    def run_tests(self):
        """运行类型测试并返回结果"""
        result = []
        result.append("=== 开始测试list和dict类型组件 ===")
        
        # 测试list类型
        result.extend(self._test_list_type())
        
        # 测试dict类型
        result.extend(self._test_dict_type())
        
        # 测试IdOrderedDict转换
        result.extend(self._test_id_ordered_dict())
        
        result.append("=== 测试完成 ===")
        
        return '\n'.join(result)
    
    def _test_list_type(self):
        """测试list类型组件"""
        result = ["\n测试list类型组件:"]
        
        # 创建list组件
        list_component = QMonoAttrItemFactory.create(self.list_attr_dict)
        
        # 获取值并检查类型
        list_value = list_component.value
        result.append(f"- 组件值: {list_value}")
        result.append(f"- 组件值类型: {type(list_value)}")
        result.append(f"- 是否为list类型: {isinstance(list_value, list)}")
        
        # 修改值后再次检查
        new_list = ['new_item1', 'new_item2']
        list_component.value = new_list
        updated_value = list_component.value
        result.append(f"- 修改后的值: {updated_value}")
        result.append(f"- 修改后的值类型: {type(updated_value)}")
        result.append(f"- 修改后是否为list类型: {isinstance(updated_value, list)}")
        
        return result
    
    def _test_dict_type(self):
        """测试dict类型组件"""
        result = ["\n测试dict类型组件:"]
        
        # 创建dict组件
        dict_component = QMonoAttrItemFactory.create(self.dict_attr_dict)
        
        # 获取值并检查类型
        dict_value = dict_component.value
        result.append(f"- 组件值: {dict_value}")
        result.append(f"- 组件值类型: {type(dict_value)}")
        result.append(f"- 是否为dict类型: {isinstance(dict_value, dict)}")
        result.append(f"- 是否为IdOrderedDict类型: {isinstance(dict_value, IdOrderedDict)}")
        
        # 检查是否可以像普通dict一样使用
        try:
            # 访问键值
            key1_value = dict_value['key1']
            result.append(f"- 成功访问键'key1': {key1_value}")
            
            # 修改键值
            dict_value['key2'] = 100
            result.append(f"- 成功修改键'key2': {dict_value['key2']}")
            
            # 添加新键值对
            dict_value['new_key'] = 'new_value'
            result.append(f"- 成功添加新键值对: {{'new_key': '{dict_value['new_key']}'}}")
            
            # 遍历键值对
            result.append(f"- 遍历键值对: {list(dict_value.items())}")
            result.append("- 可以像普通dict一样使用")
        except Exception as e:
            result.append(f"- 使用时出错: {str(e)}")
        
        return result
    
    def _test_id_ordered_dict(self):
        """测试IdOrderedDict的行为"""
        result = ["\n测试IdOrderedDict的行为:"]
        
        # 创建IdOrderedDict
        ordered_dict = IdOrderedDict({'a': 1, 'b': 2, 'c': 3})
        result.append(f"- 原始IdOrderedDict: {ordered_dict}")
        
        # 测试顺序保留
        result.append(f"- 键的顺序: {list(ordered_dict.keys())}")
        
        # 测试转换为普通dict
        regular_dict = dict(ordered_dict)
        result.append(f"- 转换为普通dict: {regular_dict}")
        result.append(f"- 转换后类型: {type(regular_dict)}")
        
        # 测试replace方法
        ordered_dict.replace('b', 'B')
        result.append(f"- 替换键'b'为'B'后: {ordered_dict}")
        result.append(f"- 替换后键的顺序: {list(ordered_dict.keys())}")
        
        return result


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("综合参数调试器")
        self.resize(1200, 900)
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 创建综合参数示例
        self.mono_attrs = self._create_comprehensive_example()
        self.mono_obj = Mono(self.mono_attrs)
        
        # 创建检查器
        self.inspector = QMonoInspector(self.mono_obj)
        layout.addWidget(self.inspector)
        
        # 设置类型测试功能
        self._setup_type_tester(layout)
    
    def _setup_type_tester(self, layout):
        """设置类型测试功能"""
        # 创建按钮布局
        buttons_layout = QVBoxLayout()
        
        # 注：测试按钮现在通过MonoAttr定义，会在inspector中显示
        # 这里保留结果显示区域，但不再直接创建按钮
        
        layout.addLayout(buttons_layout)
        
        # 创建结果显示区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        
        scroll_area.setWidget(self.result_text)
        layout.addWidget(scroll_area)
        
        # 初始化测试器
        self.type_tester = ListDictTypeTester()
    
    def _run_type_test(self):
        """运行类型测试"""
        self.result_text.clear()
        result = []
        result.append("=== 类型测试结果 ===")
        result.append(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result.append("")
        
        # 测试不同类型
        try:
            # 尝试获取mono_attrs属性
            if hasattr(self, 'mono_attrs'):
                for attr in self.mono_attrs:
                    try:
                        attr_name = attr.name
                        attr_value = attr.value
                        attr_type = type(attr_value)
                        result.append(f"- 名称: {attr_name}, 值: {attr_value}, 类型: {attr_type}")
                    except Exception as e:
                        result.append(f"- 获取属性时出错: {str(e)}")
            else:
                result.append("未找到mono_attrs属性")
            
            # 测试列表类型
            test_list = [1, "text", True, 3.14]
            result.append(f"\n列表测试: {test_list}")
            result.append(f"列表类型: {type(test_list)}")
            for i, item in enumerate(test_list):
                result.append(f"  元素{i}: 值={item}, 类型={type(item)}")
            
            # 测试字典类型
            test_dict = {"key1": "value1", "key2": 123, "key3": False}
            result.append(f"\n字典测试: {test_dict}")
            result.append(f"字典类型: {type(test_dict)}")
            for key, value in test_dict.items():
                result.append(f"  键'{key}': 值={value}, 类型={type(value)}")
            
            result.append("\n=== 测试完成 ===")
        except Exception as e:
            result.append(f"测试过程中出错: {str(e)}")
        
        self.result_text.setPlainText('\n'.join(result))
        
    def _output_vs_data(self):
        """输出VS数据"""
        self.result_text.clear()
        result = []
        result.append("=== VS数据输出 ===")
        result.append(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result.append("")
        
        try:
            if hasattr(self, 'mono_attrs'):
                for attr in self.mono_attrs:
                    try:
                        attr_name = attr.name
                        # 输出格式: inspector.vs.xxx
                        result.append(f"{attr_name}: {getattr(self.inspector.vs, attr_name)}")
                    except Exception as e:
                        result.append(f"输出属性时出错: {str(e)}")
            else:
                result.append("未找到mono_attrs属性")
            
            result.append("\n=== 输出完成 ===")
        except Exception as e:
            result.append(f"输出VS数据时出错: {str(e)}")
        
        self.result_text.setPlainText('\n'.join(result))
    
    def _assign_random_data(self):
        """为不同的attr_name赋予随机的同类型数据"""
        self.result_text.clear()
        result = []
        result.append("=== 随机数据赋值结果 ===")
        result.append(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result.append("")
        
        try:
            if hasattr(self, 'mono_attrs'):
                # 为每个属性生成并设置随机数据
                for attr in self.mono_attrs:
                    try:
                        attr_name = attr.name
                        attr_value = attr.value
                        attr_type = type(attr_value)
                        
                        # 根据不同类型生成随机数据
                        if attr_type == str:
                            # 生成随机字符串
                            random_value = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
                        elif attr_type == int:
                            # 生成随机整数
                            if hasattr(attr, 'range') and attr.range:
                                # 如果有范围限制，在范围内生成
                                random_value = random.randint(attr.range[0], attr.range[1])
                            else:
                                random_value = random.randint(-1000, 1000)
                        elif attr_type == float:
                            # 生成随机浮点数
                            if hasattr(attr, 'range') and attr.range:
                                random_value = random.uniform(attr.range[0], attr.range[1])
                            else:
                                random_value = random.uniform(-100.0, 100.0)
                        elif attr_type == bool:
                            # 生成随机布尔值
                            random_value = random.choice([True, False])
                        elif attr_type == list:
                            # 生成随机列表
                            if not attr_value:
                                # 空列表默认生成字符串列表
                                random_value = [''.join(random.choices(string.ascii_letters, k=5)) for _ in range(3)]
                            else:
                                # 根据列表中第一个元素的类型生成
                                elem_type = type(attr_value[0])
                                random_value = []
                                for _ in range(random.randint(1, 5)):
                                    if elem_type == str:
                                        random_value.append(''.join(random.choices(string.ascii_letters, k=5)))
                                    elif elem_type == int:
                                        random_value.append(random.randint(0, 100))
                                    elif elem_type == float:
                                        random_value.append(random.uniform(0.0, 100.0))
                                    elif elem_type == bool:
                                        random_value.append(random.choice([True, False]))
                                    else:
                                        # 其他类型保持不变
                                        random_value = attr_value
                                        break
                        elif attr_type == dict or 'IdOrderedDict' in str(attr_type):
                            # 生成随机字典
                            if not attr_value:
                                # 空字典默认生成
                                random_value = {}
                                for i in range(3):
                                    key = f"key_{i+1}"
                                    random_value[key] = ''.join(random.choices(string.ascii_letters, k=5))
                            else:
                                # 根据现有字典的值类型生成
                                random_value = {}
                                for key, value in attr_value.items():
                                    val_type = type(value)
                                    if val_type == str:
                                        random_value[key] = ''.join(random.choices(string.ascii_letters, k=5))
                                    elif val_type == int:
                                        random_value[key] = random.randint(0, 100)
                                    elif val_type == float:
                                        random_value[key] = random.uniform(0.0, 100.0)
                                    elif val_type == bool:
                                        random_value[key] = random.choice([True, False])
                                    else:
                                        # 其他类型保持原值
                                        random_value[key] = value
                        elif attr_type == datetime:
                            # 生成随机日期时间
                            days = random.randint(-365, 365)
                            random_value = datetime.now() + timedelta(days=days)
                        else:
                            # 其他未处理类型保持不变
                            random_value = attr_value
                            result.append(f"- 名称: {attr_name}, 类型: {attr_type} (未处理)")
                            continue
                        
                        # 设置随机值
                        # attr.value = random_value
                        setattr(self.inspector.vs, attr_name, random_value)
                        
                        # 添加结果信息
                        result.append(f"- 名称: {attr_name}, 原始值: {attr_value}")
                        result.append(f"  新随机值: {random_value}")
                        result.append(f"  类型: {attr_type}")
                    except Exception as e:
                        result.append(f"- 设置属性 {attr_name} 随机值时出错: {str(e)}")
                
                # 通知检查器更新
                if hasattr(self, 'inspector'):
                    try:
                        # 值应该会自动更新到界面
                        pass
                    except Exception as refresh_error:
                        # 捕获任何错误，确保程序继续运行
                        pass
            else:
                result.append("未找到mono_attrs属性")
            
            result.append("\n=== 赋值完成 ===")
        except Exception as e:
            result.append(f"赋值过程中出错: {str(e)}")
        
        self.result_text.setPlainText('\n'.join(result))
    
    def _create_comprehensive_example(self):
        """创建真实场景的综合参数示例，测试所有组件类型"""
        # 获取MainWindow实例的引用
        main_window = self
        
        # 定义测试函数
        def run_type_test():
            main_window._run_type_test()
            
        def output_vs_data():
            main_window._output_vs_data()
            
        def assign_random_data():
            main_window._assign_random_data()
            
        return [
            # 页面标题
            MonoAttr("app_title", "MonoWidget 综合测试", title="MonoWidget 综合参数调试器"),
            
            # 用户配置 - 使用分组
            MonoAttr("username", "Alice_Workspace", label="用户名", group="用户信息", header="👤 用户配置"),
            MonoAttr("user_id", 1001, range=(1000, 10000, 1), label="用户ID", group="用户信息"),
            MonoAttr("email", "alice@example.com", label="邮箱地址", group="用户信息"),
            
            # 应用设置
            MonoAttr("theme", "dark", enum=["light", "dark", "auto"], label="界面主题", group="外观设置", header="⚙️ 应用设置"),
            MonoAttr("language", "zh-CN", enum=["zh-CN", "en-US", "ja-JP"], label="语言", group="外观设置"),
            MonoAttr("auto_save", True, label="自动保存", group="功能设置"),
            MonoAttr("save_interval", 5, range=(1, 61, 1), label="保存间隔(分钟)", group="功能设置"),
            
            # 界面设置
            MonoAttr("window_width", 1200, range=(800, 2000, 10), label="窗口宽度", group="窗口设置", header="🖥️ 界面设置"),
            MonoAttr("window_height", 800, range=(600, 1200, 10), label="窗口高度", group="窗口设置"),
            MonoAttr("opacity", 0.95, range=(0.1, 1.0, 0.05), label="窗口透明度", group="窗口设置"),
            
            # 性能设置
            MonoAttr("max_threads", 4, range=(1, 32, 1), label="最大线程数", group="性能优化", header="🚀 性能设置"),
            MonoAttr("cache_size", 512, range=(64, 8192, 64), label="缓存大小(MB)", group="性能优化"),
            
            # 通知设置
            MonoAttr("enable_notifications", True, label="启用通知", group="通知配置", header="🔔 通知设置"),
            MonoAttr("sound_volume", 0.7, range=(0.0, 1.0, 0.1), label="音量", group="通知配置"),
            
            # 数据配置
            MonoAttr("api_timeout", 30, range=(5, 300, 5), label="API超时(秒)", group="网络设置", header="📊 数据配置"),
            MonoAttr("retry_count", 3, range=(0, 10, 1), label="重试次数", group="网络设置"),
            
            # 时间相关 - 使用改进的日历组件
            MonoAttr("created_date", datetime(2024, 1, 15, 9, 30), label="创建时间", group="时间配置", header="📅 时间设置"),
            MonoAttr("last_modified", datetime.now(), label="最后修改", group="时间配置"),
            MonoAttr("backup_time", datetime(2024, 12, 25, 2, 0), label="备份时间", group="时间配置"),
            
            # 复杂类型测试
            MonoAttr("config_hash", 12345 + 67890j, label="配置哈希", group="安全配置", header="🔧 高级设置"),
            MonoAttr("encryption_key", 3.1415926535 + 2.7182818284j, label="加密密钥", group="安全配置"),
            
            # 列表类型测试
            MonoAttr("string_list", ["item1", "item2", "item3"], label="字符串列表", group="列表示例", header="📋 列表类型"),
            MonoAttr("number_list", [1, 2, 3, 4, 5], label="数字列表", group="列表示例"),
            MonoAttr("mixed_list", ["text", 123, True, 3.14], label="混合类型列表", group="列表示例"),
            
            # 字典类型测试
            MonoAttr("simple_dict", {'key1': 'value1', 'key2': 42}, label="简单字典", group="字典示例", header="📚 字典类型"),
            MonoAttr("complex_dict", {'user': {'name': 'Alice', 'age': 30}, 'settings': {'theme': 'dark'}}, label="复杂嵌套字典", group="字典示例"),
            
            # 枚举测试
            MonoAttr("log_level", "INFO", enum=["DEBUG", "INFO", "WARNING", "ERROR"], label="日志级别", group="系统选项", header="🎨 枚举选项"),
            MonoAttr("color_scheme", "blue", enum=["red", "green", "blue", "purple", "orange"], label="配色方案", group="系统选项"),
            MonoAttr("font_size", 14, enum=[12, 14, 16, 18, 20], label="字体大小", group="系统选项"),
            MonoAttr("zoom_level", 1.0, enum=[0.5, 0.75, 1.0, 1.25, 1.5, 2.0], label="缩放级别", group="系统选项"),
            
            # 测试功能按钮（使用MonoAttr形式）
            MonoAttr("test_type_button", run_type_test, label="运行类型测试", group="测试功能", header="🧪 测试工具"),
            MonoAttr("output_vs_button", output_vs_data, label="输出VS数据", group="测试功能"),
            MonoAttr("random_data_button", assign_random_data, label="赋予随机同类型数据", group="测试功能"),
        ]


if __name__ == "__main__":
    # 创建一个应用程序实例
    app = QApplication(sys.argv)
    
    # 使用MainWindow类，它已经包含了完整的示例和类型测试功能
    win = MainWindow()
    win.show()
    
    # 启动应用程序的事件循环
    sys.exit(app.exec())