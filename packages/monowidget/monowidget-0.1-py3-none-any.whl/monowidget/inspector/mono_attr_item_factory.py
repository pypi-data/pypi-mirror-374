import sys
import os
from typing import Any
from datetime import datetime

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox, QPushButton, QComboBox

from .ui_classes import QMonoWithoutBorder

# 导入各个类型的专用类
from typing import Type, List
from PyQt6.QtCore import QDateTime
from .mono_attr_item_base import QMonoAttrItemBase
from .mono_attr_item_int import QMonoAttrItemInt
from .mono_attr_item_float import QMonoAttrItemFloat
from .mono_attr_item_str import QMonoAttrItemStr
from .mono_attr_item_bool import QMonoAttrItemBool
from .mono_attr_item_complex import QMonoAttrItemComplex
from .mono_attr_item_datetime import QMonoAttrItemDateTime
from .mono_attr_item_list import QMonoAttrItemList
from .mono_attr_item_dict import QMonoAttrItemDict
from .mono_attr_item_function import QMonoAttrFunctionItem
# 导入IdOrderedDict类型
from monowidget._utils import *


class QMonoAttrItemFactory:
    """MonoAttrItem组件工厂类
    
    根据数据类型创建对应的属性编辑组件
    """
    
    _type_mapping = {
        int: QMonoAttrItemInt,
        float: QMonoAttrItemFloat,
        str: QMonoAttrItemStr,
        bool: QMonoAttrItemBool,
        complex: QMonoAttrItemComplex,
        datetime: QMonoAttrItemDateTime,
        list: QMonoAttrItemList,
        dict: QMonoAttrItemDict,
        IdOrderedDict: QMonoAttrItemDict,  # 添加对IdOrderedDict类型的支持
        # 使用类型标识符'function'来注册函数按钮类型
        'function': QMonoAttrFunctionItem
    }
    
    @classmethod
    def create(cls, attr_dict: dict, parent=None, *, border=None):
        """创建对应的属性编辑组件
        
        Args:
            attr_dict: 属性字典，必须包含'type'键
            parent: 父组件
            border: 边框类
            
        Returns:
            对应类型的属性编辑组件
            
        Raises:
            ValueError: 当attr_dict不包含'type'键或类型不支持时
        """
        
        if 'type' not in attr_dict:
            raise ValueError("attr_dict must contain 'type' key")
            
        attr_type = attr_dict['type']
        
        if attr_type not in cls._type_mapping:
            raise ValueError(f"Unsupported type: {attr_type}")
            
        component_class = cls._type_mapping[attr_type]
        
        # 创建组件
        try:
            component = component_class(attr_dict, parent, border=border)
            return component
        except Exception as e:
            raise
        
    @classmethod
    def create_item(cls, attr_dict: dict, parent=None, *, border=None):
        """create方法的别名，用于向后兼容"""
        return cls.create(attr_dict, parent, border=border)
    
    @classmethod
    def get_supported_types(cls):
        """获取支持的类型列表"""
        return list(cls._type_mapping.keys())
    
    @classmethod
    def register_type(cls, type_class: Type, component_class: Type):
        """注册新的类型支持
        
        Args:
            type_class: Python类型类（如int, str等）
            component_class: 对应的组件类，必须继承自QMonoAttrItemBase
        """
        cls._type_mapping[type_class] = component_class

# 为了保持向后兼容性，保留原始的 QMonoAttrItem 类
class QMonoAttrItem(QWidget):
    """
    向后兼容的通用组件类
    使用工厂模式根据类型自动选择合适的实现
    """
    paramChanged = pyqtSignal(str, object)
    
    def __init__(self, attr_dict: dict, parent=None, *, border=QMonoWithoutBorder):
        super().__init__(parent)
        self._actual_item = QMonoAttrItemFactory.create_item(attr_dict, parent, border=border)
        self._actual_item.paramChanged.connect(self.paramChanged.emit)
        
        # 复制必要属性
        self.ad = attr_dict
        self._name = attr_dict['name']
        self._value = attr_dict['value']
        
    @property
    def name(self):
        return self._name
        
    @property
    def value(self):
        return self._actual_item.value
        
    @value.setter
    def value(self, v):
        self._actual_item.value = v
        
    def __getattr__(self, name):
        """代理所有其他属性访问到实际组件"""
        return getattr(self._actual_item, name)
        
    def __setattr__(self, name, value):
        """代理属性设置"""
        if name in ['_actual_item', 'ad', '_name', '_value']:
            super().__setattr__(name, value)
        else:
            if hasattr(self, '_actual_item') and hasattr(self._actual_item, name):
                setattr(self._actual_item, name, value)
            else:
                super().__setattr__(name, value)