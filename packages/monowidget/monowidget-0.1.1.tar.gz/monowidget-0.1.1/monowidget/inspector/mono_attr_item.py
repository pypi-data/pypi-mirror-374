import sys
import os
from typing import Any

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox, QPushButton, QComboBox

# 优先从 _utils 导入
try:
    from monowidget._utils import MONO_FONT
except ImportError:
    # 本地实现
    MONO_FONT = None

from .ui_classes import QMonoWithoutBorder
from .mono_attr_item_factory import QMonoAttrItemFactory

class QMonoAttrItem(QWidget):
    """
    向后兼容的通用组件类
    使用工厂模式根据类型自动选择合适的实现
    """
    paramChanged = pyqtSignal(str, object)
    
    def __init__(self, attr_dict: dict, parent=None, *, border=QMonoWithoutBorder):
        super().__init__(parent)
        self._actual_item = QMonoAttrItemFactory.create(attr_dict, parent, border=border)
        self._actual_item.paramChanged.connect(self.paramChanged.emit)
        
        # 复制必要属性
        self.ad = attr_dict
        self._name = attr_dict['name']
        self._value = attr_dict['value']
        
        # 设置布局
        self._rootL = QVBoxLayout()
        self._rootL.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._rootL)
        self._rootL.addWidget(self._actual_item)
        
    @property
    def name(self):
        return self._name
        
    @property
    def value(self):
        return self._actual_item.value
        
    @value.setter
    def value(self, v):
        self._actual_item.value = v
        
    @property
    def readonly(self):
        return self.ad['readonly']
        
    def __getattr__(self, name):
        """代理所有其他属性访问到实际组件"""
        return getattr(self._actual_item, name)
        
    def __setattr__(self, name, value):
        """代理属性设置"""
        if name in ['_actual_item', 'ad', '_name', '_value', '_rootL']:
            super().__setattr__(name, value)
        else:
            if hasattr(self, '_actual_item') and hasattr(self._actual_item, name):
                setattr(self._actual_item, name, value)
            else:
                super().__setattr__(name, value)