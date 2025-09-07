import sys
import os
from typing import Any

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QLineEdit

# 优先从 _utils 导入
try:
    from monowidget._utils import MONO_FONT
except ImportError:
    # 本地实现
    MONO_FONT = None

from .mono_attr_item_base import QMonoAttrItemBase

class QMonoAttrItemComplex(QMonoAttrItemBase):
    """复数类型专用组件"""

    def __init__(self, attr_dict: dict, parent=None, *, border=None):
        super().__init__(attr_dict, parent, border=border)
        
    def _create_type_specific_ui(self):
        """创建复数类型特定的UI元素"""
        from PyQt6.QtWidgets import QLineEdit
        
        # 创建复数输入框
        self._mwd = QLineEdit()
        if MONO_FONT:
            self._mwd.setFont(MONO_FONT)
        self._mainL.insertWidget(1, self._mwd)
        self._add_ui_to_list(self._mwd)

        # 创建枚举下拉框
        self._mcb = self._create_enum_combo()
        
        # 枚举模式设置
        if self.ad.get('enum'):
            self._mwd.setReadOnly(True)
            # 设置枚举模式下lineedit的背景颜色为更浅的灰色
            self._mwd.setStyleSheet("QLineEdit { background-color: #F4F4F4; }")

        # 连接信号
        self._mwd.textChanged.connect(self._complex_value_changed)
        if self._mcb:
            self._mcb.currentIndexChanged.connect(self._combo_value_changed)

    def _set_default_value(self, *_, value=None):
        """设置默认值"""
        value = value or self.ad['value']
        self._complex_value_changed(str(value))

    def _complex_value_changed(self, value):
        """复数值变化处理"""
        if hasattr(self, '_complex_vc_flag') and self._complex_vc_flag:
            return
        self._complex_vc_flag = True
        
        self._mwd.setText(str(value))
        try:
            self._value = complex(value)
        except ValueError:
            self._value = value
        
        self._complex_vc_flag = False
        self._param_value_changed()

    def _combo_value_changed(self, index):
        """枚举值变化处理"""
        if self.ad.get('enum'):
            value = self.ad['enum'][index]
            self._complex_value_changed(str(value))