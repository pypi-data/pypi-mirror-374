import sys
import os
from typing import Any, List

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame

from .mono_attr_item_base import QMonoAttrItemBase
from .ui_classes import QMonoWithoutBorder
from monowidget._utils import *

# 延迟导入，避免循环引用
QMonoAttrItemFactory = None

class QMonoAttrItemList(QMonoAttrItemBase):
    """列表类型专用组件
    
    用于显示和编辑列表类型的数据，每个列表元素会根据其类型使用相应的组件
    """

    def __init__(self, attr_dict: dict, parent=None, *, border=None):
        # 确保value是列表类型
        if not isinstance(attr_dict['value'], list):
            attr_dict['value'] = [attr_dict['value']] if attr_dict['value'] is not None else []
        
        # 先初始化列表相关属性
        self._list_items = []  # 存储列表元素的组件
        self._list_layout = None  # 列表布局
        
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
        """重写基类方法，列表组件不需要在_mainL中添加标签"""
        # 不添加任何UI元素到_mainL中
        pass
        
    def _create_type_specific_ui(self):
        """创建列表类型特定的UI元素"""
        
        # 创建列表容器布局
        self._list_layout = QVBoxLayout()
        self._list_layout.setContentsMargins(8, 20, 8, 8)  # 顶部留出空间给变量名
        self._list_layout.setSpacing(4)
        
        # 创建添加按钮
        add_btn = QPushButton("+ 添加元素")
        add_btn.setFixedHeight(28)
        add_btn.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 4px; color: #333;")
        add_btn.clicked.connect(self._add_list_item)
        
        # 创建一个新的垂直布局来容纳列表和添加按钮
        list_content_layout = QVBoxLayout()
        list_content_layout.addLayout(self._list_layout)
        list_content_layout.addWidget(add_btn)
        
        # 将整个列表内容布局添加到根布局（垂直布局）
        self._rootL.addLayout(list_content_layout)
        
        # 初始填充列表元素
        self._refresh_list_items()

    def _refresh_list_items(self):
        """刷新列表元素的显示"""
        # 清空现有列表元素
        for i in reversed(range(self._list_layout.count())):
            item = self._list_layout.itemAt(i)
            if item.widget():
                widget = item.widget()
                self._list_layout.removeWidget(widget)
                widget.deleteLater()
        
        self._list_items.clear()
        
        # 添加新的列表元素
        for index, item_value in enumerate(self._value):
            self._add_existing_list_item(index, item_value)

    def _add_existing_list_item(self, index: int, item_value: Any):
        """添加已存在的列表元素到UI"""
        # 创建元素容器
        item_container = QFrame()
        item_container.setFrameShape(QFrame.Shape.NoFrame)
        item_container.setStyleSheet("background-color: transparent;")
        
        # 创建元素布局
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(4, 4, 4, 4)
        item_layout.setSpacing(6)
        item_container.setLayout(item_layout)
        
        # 添加索引标签
        index_label = QLabel(f"[{index}]")
        index_label.setFixedWidth(30)
        index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        index_label.setStyleSheet("font-size: 12px; color: #666;")
        item_layout.addWidget(index_label)
        
        # 延迟导入QMonoAttrItemFactory
        global QMonoAttrItemFactory
        if QMonoAttrItemFactory is None:
            from .mono_attr_item_factory import QMonoAttrItemFactory
        
        # 根据元素类型创建对应的组件
        item_type = type(item_value)
        
        # 创建适合当前元素类型的属性字典
        item_attr_dict = {
            'name': f"{self._name}[{index}]",  # 使用索引表示法，更清晰
            'value': item_value,
            'type': item_type,
            'label': '',  # 不显示元素类型作为标签
            'readonly': self.ad.get('readonly', False),
            'show_name': False  # 不显示名称
        }
        
        # 为不同类型的元素添加特定属性
        if isinstance(item_value, (int, float)) and 'range' in self.ad:
            # 对于数值类型，可以继承父列表的range属性
            item_attr_dict['range'] = self.ad['range']
        elif isinstance(item_value, str) and 'enum' in self.ad:
            # 对于字符串类型，可以继承父列表的enum属性
            item_attr_dict['enum'] = self.ad['enum']
        
        # 复制其他可能的属性
        for key in ['tooltip', 'enum', 'range', 'color']:
            if key in self.ad and key not in item_attr_dict:
                item_attr_dict[key] = self.ad[key]
        
        # 初始化item_widget变量
        item_widget = None
        
        # 使用工厂创建组件
        try:
            # 调用工厂方法，传递父组件的border参数
            item_widget = QMonoAttrItemFactory.create(item_attr_dict, self, border=self._border)
            # 使用IIFE模式确保index值被正确捕获
            item_widget.paramChanged.connect((lambda idx: lambda val: self._list_item_value_changed(int(idx), val))(index))
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
            type_btn.clicked.connect(lambda _, idx=index: self._change_item_type(idx))
            item_layout.addWidget(type_btn)

        # 添加删除按钮（如果不是只读模式）
        if not self.ad.get('readonly', False):
            remove_btn = QPushButton("-")
            remove_btn.setFixedSize(28, 28)
            remove_btn.setFont(QFont('Arial', 10))
            remove_btn.setStyleSheet("background-color: #f8f8f8; border: 1px solid #ddd; border-radius: 4px; color: #666;")
            remove_btn.clicked.connect(lambda _, idx=index: self._remove_list_item(idx))
            item_layout.addWidget(remove_btn)
        
        # 添加到列表布局
        self._list_layout.addWidget(item_container)
        if item_widget is not None:
            self._list_items.append((item_container, item_widget))

    def _add_list_item(self):
        """添加新的列表元素"""
        if self.ad.get('readonly', False):
            return
        
        # 默认添加一个空字符串作为新元素
        self._value.append("")
        self._refresh_list_items()
        self._emit_value_changed()

    def _remove_list_item(self, index: int):
        """移除列表元素"""
        if self.ad.get('readonly', False) or index < 0 or index >= len(self._value):
            return
        
        del self._value[index]
        self._refresh_list_items()
        self._emit_value_changed()

    def _list_item_value_changed(self, index: int, value: Any):
        """处理列表元素值的变化"""
        if index >= 0 and index < len(self._value):
            self._value[index] = value
            self._emit_value_changed()

    def _emit_value_changed(self):
        """发射值变化信号"""
        # 避免重复发射相同的值
        if self._value != self._last_emit_value:
            self._last_emit_value = self._value.copy()
            self.paramChanged.emit(self._name, self._value)
    
    def _change_item_type(self, index: int):
        """更改列表项的值类型
        
        Args:
            index: 列表项索引
        """
        if index < 0 or index >= len(self._value):
            return
            
        current_value = self._value[index]
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
            # 连接信号，使用闭包确保正确的类型和索引被传递
            action.triggered.connect(lambda checked, t=typ, idx=index: self._apply_type_change(idx, t))
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
            # 连接信号，使用闭包确保正确的类型和索引被传递
            action.triggered.connect(lambda checked, t=typ, idx=index: self._apply_type_change(idx, t))
            menu.addAction(action)
        
        # 在鼠标当前位置显示菜单
        menu.exec(QCursor.pos())
        
    def _apply_type_change(self, index: int, new_type):
        """应用类型更改
        
        Args:
            index: 列表项索引
            new_type: 新的类型
        """
        if index < 0 or index >= len(self._value):
            return
            
        current_value = self._value[index]
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
            self._value[index] = new_value
            self._refresh_list_items()
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
            
            self._value[index] = new_value
            self._refresh_list_items()
            self._emit_value_changed()

    def _set_default_value(self, *_, value=None):
        """设置默认值"""
        if value is not None:
            if not isinstance(value, list):
                value = [value]
            self._value = value
            self._refresh_list_items()
            self._emit_value_changed()
    
    def paintEvent(self, event):
        """绘制事件：添加浅色细框和变量名，实现框线穿过文字但文字区域无框线效果"""
        super().paintEvent(event)
        
        from PyQt6.QtGui import QPainter, QPen, QColor, QFont
        from PyQt6.QtCore import QRect, Qt
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 设置变量名
        variable_name = self._name
        
        # 绘制浅色细框（整个边框）
        pen = QPen(QColor(0xDD, 0xDD, 0xDD), 1)
        painter.setPen(pen)
        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.drawRect(rect)
        
        # 设置字体
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        # 计算文字位置和大小
        text_rect = painter.boundingRect(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, variable_name)
        text_rect.setX(10)  # 左边距
        text_rect.setY(2)   # 上边距
        text_rect.setHeight(16)  # 文字区域高度
        # 增加宽度，确保完整显示所有字符
        text_width = painter.fontMetrics().horizontalAdvance(variable_name) + 20  # 增加一些额外空间
        text_rect.setWidth(text_width)
        
        # 绘制背景矩形，覆盖文字区域的边框线
        painter.fillRect(text_rect, self.palette().color(self.backgroundRole()))
        
        # 在背景矩形上绘制文字
        painter.setPen(QColor(0x66, 0x66, 0x66))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, variable_name)