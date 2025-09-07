import sys
import os
from typing import Any, Dict

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QLineEdit

from .mono_attr_item_base import QMonoAttrItemBase
from .ui_classes import QMonoWithoutBorder
from monowidget._utils import *

# 延迟导入，避免循环引用
QMonoAttrItemFactory = None

class QMonoAttrItemDict(QMonoAttrItemBase):
    """字典类型专用组件
    
    用于显示和编辑字典类型的数据，每个字典项会根据其类型使用相应的组件
    """

    def __init__(self, attr_dict: dict, parent=None, *, border=None):
        # 确保value是IdOrderedDict类型
        if not isinstance(attr_dict['value'], IdOrderedDict):
            if isinstance(attr_dict['value'], dict):
                attr_dict['value'] = IdOrderedDict(attr_dict['value'])
            else:
                attr_dict['value'] = IdOrderedDict()
        
        # 先初始化字典相关属性
        self._dict_items = []  # 存储字典项的组件
        self._dict_layout = None  # 字典布局
        
        # 确保border参数是一个类而不是实例
        # 如果border是None或字符串，则使用默认值
        if border is None or isinstance(border, str):
            border_class = QMonoWithoutBorder
        elif isinstance(border, type) and issubclass(border, QMonoWithoutBorder):
            border_class = border
        else:
            # 如果border是实例，获取其类
            border_class = type(border)
        
        # 调用父类构造函数，传入正确的border类
        super().__init__(attr_dict, parent, border=border_class)

    def _create_common_ui(self):
        """重写基类方法，字典组件不需要在_mainL中添加标签"""
        # 不添加任何UI元素到_mainL中
        pass
        
    def _create_type_specific_ui(self):
        """创建字典类型特定的UI元素"""
        
        # 创建字典容器布局
        self._dict_layout = QVBoxLayout()
        self._dict_layout.setContentsMargins(8, 20, 8, 8)  # 顶部留出空间给变量名
        self._dict_layout.setSpacing(4)
        
        # 创建添加按钮
        add_btn = QPushButton("+ 添加键值对")
        add_btn.setFixedHeight(28)
        add_btn.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 4px; color: #333;")
        add_btn.clicked.connect(self._add_dict_item)
        
        # 创建一个新的垂直布局来容纳字典和添加按钮
        dict_content_layout = QVBoxLayout()
        dict_content_layout.addLayout(self._dict_layout)
        dict_content_layout.addWidget(add_btn)
        
        # 将整个字典内容布局添加到根布局（垂直布局）
        self._rootL.addLayout(dict_content_layout)
        
        # 初始填充字典元素
        self._refresh_dict_items()

    def _refresh_dict_items(self):
        """刷新字典元素的显示"""
        # 清空现有字典元素
        for i in reversed(range(self._dict_layout.count())):
            item = self._dict_layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                self._dict_layout.removeWidget(widget)
                widget.deleteLater()
        
        self._dict_items.clear()
        
        # 添加新的字典元素
        for key, value in self._value.items():
            # 创建元素容器
            item_container = QFrame()
            item_container.setFrameShape(QFrame.Shape.NoFrame)
            item_container.setStyleSheet("background-color: transparent;")
            
            # 创建元素布局
            item_layout = QHBoxLayout()
            item_layout.setContentsMargins(4, 4, 4, 4)
            item_layout.setSpacing(6)
            item_container.setLayout(item_layout)
            
            # 添加可编辑的键输入框
            key_edit = QLineEdit(str(key))
            key_edit.setFixedWidth(100)
            key_edit.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            key_edit.setStyleSheet("font-size: 12px; color: #333;")
            # 如果是只读模式，禁用编辑
            if self.ad.get('readonly', False):
                key_edit.setEnabled(False)
            else:
                # 连接信号，当失去焦点或按下回车键时保存键的修改
                key_edit.editingFinished.connect(lambda old_key=key, edit=key_edit: self._edit_key(old_key, edit))
            item_layout.addWidget(key_edit)
            
            # 延迟导入QMonoAttrItemFactory
            global QMonoAttrItemFactory
            if QMonoAttrItemFactory is None:
                from .mono_attr_item_factory import QMonoAttrItemFactory
            
            # 根据值类型创建对应的组件
            item_type = type(value)
            
            # 创建适合当前元素类型的属性字典
            item_attr_dict = {
                'name': f"{self._name}[{key}]",  # 使用索引表示法，更清晰
                'value': value,
                'type': item_type,
                'label': '',  # 不显示元素类型作为标签
                'readonly': self.ad.get('readonly', False),
                'show_name': False  # 不显示名称
            }
            
            # 复制其他可能的属性
            for key_prop in ['tooltip', 'enum', 'range', 'color']:
                if key_prop in self.ad and key_prop not in item_attr_dict:
                    item_attr_dict[key_prop] = self.ad[key_prop]
            
            # 初始化item_widget变量
            item_widget = None
            
            # 使用工厂创建组件
            try:
                # 调用工厂方法，传递父组件的border参数
                item_widget = QMonoAttrItemFactory.create(item_attr_dict, self, border=self._border)
                # 使用IIFE模式确保key值被正确捕获
                item_widget.paramChanged.connect((lambda k: lambda val: self._dict_item_value_changed(k, val))(key))
                item_layout.addWidget(item_widget, 1)  # 使用伸展因子让组件占据剩余空间
            except Exception as e:
                # 如果创建失败，显示错误信息
                error_label = QLabel(f"创建组件失败: {str(e)}")
                error_label.setStyleSheet("color: red;")
                item_layout.addWidget(error_label, 1)
            
            # 添加类型转换按钮（如果不是只读模式）
            if not self.ad.get('readonly', False):
                type_btn = QPushButton("T")
                type_btn.setFixedSize(28, 28)
                type_btn.setFont(QFont('Arial', 10))
                type_btn.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 4px; color: #666;")
                type_btn.setToolTip("切换值类型")
                type_btn.clicked.connect(lambda _, k=key: self._change_item_type(k))
                item_layout.addWidget(type_btn)

            # 添加删除按钮（如果不是只读模式）
            if not self.ad.get('readonly', False):
                remove_btn = QPushButton("-")
                remove_btn.setFixedSize(28, 28)
                remove_btn.setFont(QFont('Arial', 10))
                remove_btn.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd; border-radius: 4px; color: #666;")
                remove_btn.clicked.connect(lambda _, k=key: self._remove_dict_item(k))
                item_layout.addWidget(remove_btn)
            
            # 添加到字典布局
            self._dict_layout.addWidget(item_container)
            if item_widget is not None:
                self._dict_items.append((item_container, item_widget))

    def _add_existing_dict_item(self, key: str, value: Any):
        """添加已存在的字典元素到UI"""
        # 创建元素容器
        item_container = QFrame()
        item_container.setFrameShape(QFrame.Shape.NoFrame)
        item_container.setStyleSheet("background-color: transparent;")
        
        # 创建元素布局
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(4, 4, 4, 4)
        item_layout.setSpacing(6)
        item_container.setLayout(item_layout)
        
        # 添加可编辑的键输入框
        key_edit = QLineEdit(str(key))
        key_edit.setFixedWidth(100)
        key_edit.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        key_edit.setStyleSheet("font-size: 12px; color: #333;")
        # 如果是只读模式，禁用编辑
        if self.ad.get('readonly', False):
            key_edit.setEnabled(False)
        else:
            # 连接信号，当失去焦点或按下回车键时保存键的修改
            key_edit.editingFinished.connect(lambda old_key=key, edit=key_edit: self._edit_key(old_key, edit))
        item_layout.addWidget(key_edit)
        
        # 延迟导入QMonoAttrItemFactory
        global QMonoAttrItemFactory
        if QMonoAttrItemFactory is None:
            from .mono_attr_item_factory import QMonoAttrItemFactory
        
        # 根据值类型创建对应的组件
        item_type = type(value)
        
        # 创建适合当前元素类型的属性字典
        item_attr_dict = {
            'name': f"{self._name}[{key}]",  # 使用索引表示法，更清晰
            'value': value,
            'type': item_type,
            'label': '',  # 不显示元素类型作为标签
            'readonly': self.ad.get('readonly', False),
            'show_name': False  # 不显示名称
        }
        
        # 复制其他可能的属性
        for key_prop in ['tooltip', 'enum', 'range', 'color']:
            if key_prop in self.ad and key_prop not in item_attr_dict:
                item_attr_dict[key_prop] = self.ad[key_prop]
        
        # 初始化item_widget变量
        item_widget = None
        
        # 使用工厂创建组件
        try:
            # 调用工厂方法，传递父组件的border参数
            item_widget = QMonoAttrItemFactory.create(item_attr_dict, self, border=self._border)
            # 使用IIFE模式确保key值被正确捕获
            item_widget.paramChanged.connect((lambda k: lambda val: self._dict_item_value_changed(k, val))(key))
            item_layout.addWidget(item_widget, 1)  # 使用伸展因子让组件占据剩余空间
        except Exception as e:
            # 如果创建失败，显示错误信息
            error_label = QLabel(f"创建组件失败: {str(e)}")
            error_label.setStyleSheet("color: red;")
            item_layout.addWidget(error_label, 1)
        
        # 添加删除按钮（如果不是只读模式）
        if not self.ad.get('readonly', False):
            remove_btn = QPushButton("-")
            remove_btn.setFixedSize(28, 28)
            remove_btn.setFont(QFont('Arial', 10))
            remove_btn.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd; border-radius: 4px; color: #666;")
            remove_btn.clicked.connect(lambda _, k=key: self._remove_dict_item(k))
            item_layout.addWidget(remove_btn)
        
        # 添加到字典布局
        self._dict_layout.addWidget(item_container)
        if item_widget is not None:
            self._dict_items.append((item_container, item_widget))

    def _add_dict_item(self):
        """添加新的字典键值对
        直接创建一个不重复的键，不再使用弹窗
        """
        if self.ad.get('readonly', False):
            return
        
        # 生成不重复的键名
        counter = 1
        while True:
            new_key = f"new_key_{counter}"
            if new_key not in self._value:
                break
            counter += 1
        
        # 默认值设置为空字符串
        default_value = ""
        
        # 添加新的键值对
        self._value[new_key] = default_value
        self._refresh_dict_items()
        self._emit_value_changed()
        
        # 调试输出
        print(f"已添加新键值对: {new_key} = {default_value}")

    def _remove_dict_item(self, key: str):
        """移除字典元素"""
        if self.ad.get('readonly', False) or key not in self._value:
            return
        
        del self._value[key]
        self._refresh_dict_items()
        self._emit_value_changed()

    def _dict_item_value_changed(self, key: str, value: Any):
        """处理字典元素值的变化"""
        if key in self._value:
            self._value[key] = value
            self._emit_value_changed()
    
    def _edit_key(self, old_key: str, key_edit: QLineEdit):
        """编辑字典的键名
        
        Args:
            old_key: 原始键名
            key_edit: 键编辑框组件
        """
        new_key = key_edit.text().strip()
        
        # 如果新键与旧键相同，不需要操作
        if old_key == new_key:
            return
        
        # 检查新键是否为空或已存在
        if not new_key:
            # 如果新键为空，恢复旧键名
            key_edit.setText(old_key)
            return
        
        if new_key in self._value:
            # 如果新键已存在，恢复旧键名并显示错误消息
            key_edit.setText(old_key)
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "错误", f"键 '{new_key}' 已存在！")
            return
        
        # 使用IdOrderedDict的replace方法替换键名
        if isinstance(self._value, IdOrderedDict):
            self._value.replace(old_key, new_key)
        else:
            # 兼容普通字典的处理方式
            value = self._value.pop(old_key)
            self._value[new_key] = value
        
        # 刷新UI显示
        self._refresh_dict_items()
        self._emit_value_changed()
        
        # 调试输出
        print(f"键 '{old_key}' 已更改为 '{new_key}'")

    def _emit_value_changed(self):
        """发射值变化信号"""
        # 避免重复发射相同的值
        self._param_value_changed()
    
    def _change_item_type(self, key):
        """更改字典项的值类型
        
        Args:
            key: 字典项的键
        """
        if key not in self._value:
            return
            
        current_value = self._value[key]
        current_type = type(current_value)
        
        # 定义支持的类型转换选项
        type_options = [
            (str, "字符串"),
            (int, "整数"),
            (float, "浮点数"),
            (bool, "布尔值")
        ]
        
        # 创建在按钮位置弹出的菜单
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction, QCursor
        
        # 创建菜单
        menu = QMenu(self)
        
        # 添加第一项空白操作
        first_action = QAction("转化类型", self)
        first_action.setDisabled(True)
        menu.addAction(first_action)
        
        # 添加分隔线
        menu.addSeparator()
        
        # 添加基本类型选项
        for typ, name in type_options:
            action = QAction(name, self)
            # 连接信号，使用闭包确保正确的类型和键被传递
            action.triggered.connect(lambda checked, t=typ, k=key: self._apply_type_change(k, t))
            menu.addAction(action)
        
        # 添加分隔线
        menu.addSeparator()
        
        # 添加复合类型选项
        complex_type_options = [
            (list, "列表"),
            (dict, "字典")
        ]
        
        for typ, name in complex_type_options:
            action = QAction(name, self)
            # 连接信号，使用闭包确保正确的类型和键被传递
            action.triggered.connect(lambda checked, t=typ, k=key: self._apply_type_change(k, t))
            menu.addAction(action)
        
        # 在鼠标当前位置显示菜单
        menu.exec(QCursor.pos())
        
    def _apply_type_change(self, key, new_type):
        """应用类型更改
        
        Args:
            key: 字典项的键
            new_type: 新的类型
        """
        if key not in self._value:
            return
            
        current_value = self._value[key]
        new_value = None  # 预先初始化new_value变量
        
        try:
            # 尝试进行类型转换
            if new_type == bool:
                # 特殊处理布尔类型转换
                if isinstance(current_value, str):
                    # 字符串转布尔值
                    new_value = current_value.lower() in ('true', 'yes', '1', 't', 'y')
                else:
                    # 其他类型转布尔值
                    new_value = bool(current_value)
            elif new_type == list:
                # 特殊处理列表类型转换
                if not isinstance(current_value, list):
                    new_value = [current_value]
                else:
                    new_value = list(current_value)
            elif new_type == dict:
                # 特殊处理字典类型转换
                if isinstance(current_value, str):
                    # 字符串尝试解析为字典，这里不做复杂解析，直接创建空字典
                    new_value = {}
                else:
                    # 其他类型转字典（简单处理）
                    try:
                        new_value = dict(current_value)
                    except:
                        # 如果无法转换，创建空字典
                        new_value = {}
            else:
                # 普通类型转换
                new_value = new_type(current_value)
            
            # 应用新值
            self._value[key] = new_value
            self._refresh_dict_items()
            self._emit_value_changed()
            
        except Exception as e:
            # 转换失败时使用空值并显示警告
            from _utils import QPop, QPWarn
            
            # 获取选中类型的名称
            type_names = {
                str: "字符串",
                int: "整数",
                float: "浮点数",
                bool: "布尔值",
                list: "列表",
                dict: "字典"
            }
            selected_type_name = type_names.get(new_type, str(new_type))
            
            QPop(QPWarn(f"无法将值 '{current_value}' 转换为 {selected_type_name}:\n{str(e)}", ct=16000))
            
            # 使用空值
            if new_type == str:
                new_value = ""
            elif new_type == int:
                new_value = 0
            elif new_type == float:
                new_value = 0.0
            elif new_type == bool:
                new_value = False
            elif new_type == list:
                new_value = []
            elif new_type == dict:
                new_value = {}
            
            self._value[key] = new_value
            self._refresh_dict_items()
            self._emit_value_changed()

    @property
    def value(self):
        """当前值 - 返回普通dict类型"""
        if isinstance(self._value, IdOrderedDict):
            return dict(self._value)
        return self._value

    @value.setter
    def value(self, v):
        """设置值 - 自动将dict转换为IdOrderedDict，并确保UI立即更新"""
        self._set_default_value(value=v)
        
    def _set_default_value(self, *_, value=None):
        """设置默认值 - 自动处理dict到IdOrderedDict的转换，并确保UI更新"""
        # 保存原始值，用于比较
        old_value = self._value.copy() if self._value else None
        
        # 处理传入的值
        value = value or self.ad['value']
        if not isinstance(value, IdOrderedDict):
            if isinstance(value, dict):
                value = IdOrderedDict(value)
            else:
                value = IdOrderedDict()
        
        # 更新内部值
        self._value = value
        
        # 刷新字典项显示
        self._refresh_dict_items()
        
        # 触发值变化信号
        if old_value != self._value:
            self._param_value_changed()
        
        # 强制更新UI
        self.update()
        self.repaint()