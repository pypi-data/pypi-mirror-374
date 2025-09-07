import sys
import os
from typing import Any

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QDoubleSpinBox, QComboBox

# 优先从 _utils 导入
try:
    from monowidget._utils import QDoubleSlider, MONO_FONT
    from monowidget._utils import find_value_enum_closest
except ImportError:
    # 本地实现
    QDoubleSlider = None
    MONO_FONT = None
    
    def find_value_enum_closest(value, enum_list):
        """找到最接近的枚举值"""
        if not enum_list:
            return 0, value
        try:
            closest = min(enum_list, key=lambda x: abs(float(x) - float(value)))
            return enum_list.index(closest), closest
        except:
            return 0, value

from .mono_attr_item_base import QMonoAttrItemBase

class QMonoAttrItemFloat(QMonoAttrItemBase):
    """浮点数类型专用组件"""

    def __init__(self, attr_dict: dict, parent=None, *, border=None):
        super().__init__(attr_dict, parent, border=border)
        
    def _create_type_specific_ui(self):
        """创建浮点数类型特定的UI元素"""
        from PyQt6.QtWidgets import QDoubleSpinBox
        
        # 初始化属性
        self._mcb = None
        self._mwd = None
        self._qsl = None
        
        # 检查是否为枚举类型
        if self.ad.get('enum'):
            # 枚举模式：只显示下拉框
            self._mcb = self._create_enum_combo()
            if self._mcb:
                self._mainL.insertWidget(1, self._mcb)
                self._add_ui_to_list(self._mcb)
        else:
            # 普通模式：显示输入框和滑块
            self._mwd = QDoubleSpinBox()
            if MONO_FONT:
                self._mwd.setFont(MONO_FONT)
            self._mainL.insertWidget(1, self._mwd)
            self._add_ui_to_list(self._mwd)

            # 创建范围滑块
            self._qsl = self._create_range_slider(0.0, 100.0, 0.01, QDoubleSlider)
            
            # 设置范围
            if self.ad.get('range'):
                start, stop, step = self.ad['range'].start, self.ad['range'].stop, self.ad['range'].step
                start, stop, step = start or 0.0, stop, step or 0.01
                self._mwd.setRange(start, stop)
                self._mwd.setSingleStep(step)
            
            # 连接信号
            self._mwd.valueChanged.connect(self._int_float_value_changed)
            if self._qsl:
                self._qsl.monoChanged.connect(self._int_float_value_changed)
        
        # 枚举下拉框连接信号（如果存在）
        if self._mcb and self.ad.get('enum'):
            self._mcb.currentIndexChanged.connect(self._combo_value_changed)

    def _set_default_value(self, *_, value=None):
        """设置默认值"""
        value = value or self.ad['value']
        self._int_float_value_changed(value)

    def _int_float_value_changed(self, value, *args):
        """浮点数值变化处理"""
        if hasattr(self, '_int_float_vc_flag') and self._int_float_vc_flag:
            return
        self._int_float_vc_flag = True
        
        if self.ad.get('enum'):
            # 枚举模式
            if self._mcb:
                idx, value = find_value_enum_closest(value, self.ad['enum'])
                self._mcb.setCurrentIndex(idx)
        else:
            # 普通模式
            if self._mcb and self.ad.get('enum'):
                idx, value = find_value_enum_closest(value, self.ad['enum'])
                self._mcb.setCurrentIndex(idx)
            
            if hasattr(self, '_mwd') and self._mwd:
                self._mwd.setValue(value)
            if hasattr(self, '_qsl') and self._qsl:
                self._qsl.setValue(value)
        
        self._value = value
        self._int_float_vc_flag = False
        self._param_value_changed()

    def _combo_value_changed(self, index):
        """枚举值变化处理"""
        if self.ad.get('enum'):
            value = self.ad['enum'][index]
            self._int_float_value_changed(value)