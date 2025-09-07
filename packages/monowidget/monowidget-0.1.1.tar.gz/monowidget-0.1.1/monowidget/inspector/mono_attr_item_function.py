import sys
import os
from typing import Any, Callable

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QPushButton, QLabel

# 优先从 _utils 导入
try:
    from monowidget._utils import MONO_FONT
except ImportError:
    # 本地实现
    MONO_FONT = None

from .mono_attr_item_base import QMonoAttrItemBase

class QMonoAttrFunctionItem(QMonoAttrItemBase):
    """函数按钮类型专用组件
    只由一个按钮组成，没有复位按钮
    """

    def __init__(self, attr_dict: dict, parent=None, *, border=None):
        # 确保attr_dict包含必要的键
        if 'function' not in attr_dict:
            raise ValueError("attr_dict must contain 'function' key")
            
        # 确保args和kwargs参数存在且为列表和字典
        if 'args' not in attr_dict:
            attr_dict['args'] = []
        if 'kwargs' not in attr_dict:
            attr_dict['kwargs'] = {}
        
        # 如果没有显式设置show_name，默认设置为False，不显示名称标签
        if 'show_name' not in attr_dict:
            attr_dict['show_name'] = False
        
        super().__init__(attr_dict, parent, border=border)
        
    def _create_common_ui(self):
        """创建公共UI元素
        重写父类方法，不添加复位按钮
        """
        # 标签 - 只有当show_name不为False时才显示
        show_name = self.ad.get('show_name', True)  # 默认显示名称
        if show_name:
            self._lbl = QLabel(self.ad['label'] if self.ad['label'] else self.ad['name'])
            if MONO_FONT:
                self._lbl.setFont(MONO_FONT)
            self._mainL.addWidget(self._lbl)
            self._uis.append(self._lbl)
        else:
            self._lbl = None
        
        # 不添加复位按钮，这是与其他组件的主要区别
        self._btn = None

    def _create_type_specific_ui(self):
        """创建函数按钮类型特定的UI元素"""
        # 确定按钮名称：优先使用label，其次使用name
        button_text = self.ad.get('label', self.ad.get('name', 'Button'))
        # 创建功能按钮
        self._mwd = QPushButton(button_text)
        if MONO_FONT:
            self._mwd.setFont(MONO_FONT)
        
        # 将按钮添加到布局中
        if self._lbl:
            self._mainL.insertWidget(1, self._mwd)
        else:
            self._mainL.addWidget(self._mwd)
            
        self._add_ui_to_list(self._mwd)

        # 连接按钮点击信号到指定函数
        self._mwd.clicked.connect(self._function_clicked)

    def _set_default_value(self, *_, value=None):
        """设置默认值
        对于函数按钮类型，这个方法不做实际操作，因为按钮不存储值
        """
        # 函数按钮不存储值，所以不需要设置
        pass

    def _function_clicked(self):
        """处理按钮点击事件，调用指定的函数"""
        # 调用attr_dict中指定的函数
        if callable(self.ad['function']):
            # 获取可能存在的args参数
            args = self.ad.get('args', [])
            kwargs = self.ad.get('kwargs', {})
            # 调用函数并传递参数
            self.ad['function'](*args, **kwargs)

    def _param_value_changed(self):
        """参数值变化处理
        对于函数按钮类型，这个方法通常不被调用，因为按钮不存储值
        """
        # 函数按钮不存储值，所以不需要发出信号
        pass

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._border and hasattr(self._border, 'paint'):
            self._border.paint(self, event)