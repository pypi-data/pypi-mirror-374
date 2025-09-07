import sys
import os
from typing import Any

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QCheckBox

# 优先从 _utils 导入
try:
    from monowidget._utils import MONO_FONT
except ImportError:
    # 本地实现
    MONO_FONT = None

from .mono_attr_item_base import QMonoAttrItemBase

class QMonoAttrItemBool(QMonoAttrItemBase):
    """布尔类型专用组件"""

    def __init__(self, attr_dict: dict, parent=None, *, border=None):
        super().__init__(attr_dict, parent, border=border)
        
    def _create_type_specific_ui(self):
        """创建布尔类型特定的UI元素"""
        from PyQt6.QtWidgets import QCheckBox
        
        # 创建复选框
        self._mcb = QCheckBox()
        self._mainL.insertWidget(1, self._mcb)
        self._add_ui_to_list(self._mcb)

        # 连接信号
        self._mcb.stateChanged.connect(self._bool_value_changed)

    def _set_default_value(self, *_, value=None):
        """设置默认值"""
        value = value or self.ad['value']
        self._bool_value_changed(Qt.CheckState.Checked if value else Qt.CheckState.Unchecked)

    def _bool_value_changed(self, state):
        """布尔值变化处理"""
        self._value = bool(state)
        self._param_value_changed()

    def _param_value_changed(self):
        if self._last_emit_value == self._value: return
        self._last_emit_value = self._value
        self.paramChanged.emit(self._name, self._value)