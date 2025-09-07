import sys
import os
from typing import Any

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

# 优先从 _utils 导入
try:
    from _utils import *
except ImportError:
    # 本地实现
    MONO_FONT = None
    from PyQt6.QtWidgets import QPushButton
    class QMonoResetButton(QPushButton):
        def __init__(self, parent=None):
            super().__init__("↻", parent)
            self.setFixedSize(28, 28)  # 从22改为28
            self.setFont(QFont('Arial', 10))

from .ui_classes import QMonoWithoutBorder

class QMonoAttrItemBase(QWidget):
    """
    MonoAttrItem 的基础父类
    抽取所有类型组件的公共部分
    """
    paramChanged = pyqtSignal(str, object)

    def __init__(self, attr_dict: dict, parent=None, *, border=QMonoWithoutBorder):
        super().__init__(parent)
        self.ad = attr_dict
        self._name = self.ad['name']
        self._value = self.ad['value']
        self._last_emit_value = self._value
        
        # 公共UI元素
        self._rootL = QVBoxLayout()
        self._rootL.setContentsMargins(4, 4, 6, 6)
        self._rootL.setSpacing(4)
        self._mainL = QHBoxLayout()
        self._mainL.setContentsMargins(2, 2, 4, 4)
        self._mainL.setSpacing(2)
        
        # 设置布局
        self.setLayout(self._rootL)
        self._rootL.addLayout(self._mainL)
        
        # 边框样式
        self._border = border
        assert issubclass(self._border, QMonoWithoutBorder), "Border must be subclass of QMonoWithoutBorder."
        
        # 公共UI组件
        self._lbl = None
        self._btn = None
        self._uis = []
        
        # 创建公共UI
        self._create_common_ui()
        
        # 子类需要实现的部分
        self._create_type_specific_ui()
        self._set_default_value()
        
        # 在子类创建完特定UI后，将复位按钮添加到最右侧
        if self._btn:
            # 先移除原有的复位按钮
            index = self._mainL.indexOf(self._btn)
            if index != -1:
                self._mainL.removeWidget(self._btn)
            # 添加到最右侧
            self._mainL.addWidget(self._btn)

    @property
    def name(self):
        """属性名称"""
        return self._name

    @property
    def value(self):
        """当前值"""
        return self._value

    @value.setter
    def value(self, v):
        """设置值"""
        self._set_default_value(value=v)

    @property
    def readonly(self):
        """是否只读"""
        return self.ad['readonly']

    def _create_common_ui(self):
        """创建公共UI元素"""
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
        
        # 重置按钮
        self._btn = QMonoResetButton()
        self._btn.clicked.connect(self._set_default_value)
        self._mainL.addWidget(self._btn)
        
        # 将公共组件添加到UI列表
        self._uis.append(self._btn)

    def _create_type_specific_ui(self):
        """
        子类必须实现：创建类型特定的UI元素
        """
        raise NotImplementedError("子类必须实现 _create_type_specific_ui 方法")

    def _set_default_value(self, *_, value=None):
        """
        子类必须实现：设置默认值
        """
        raise NotImplementedError("子类必须实现 _set_default_value 方法")

    def _apply_common_styles(self):
        """应用公共样式"""
        # 半透明背景
        for ui in self._uis:
            ui.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 设置标签文本
        if self.ad['label']:
            self._lbl.setText(self.ad['label'])

        # 只读状态
        if self.ad['readonly']:
            for ui in self._uis:
                ui.setEnabled(False)

        # 工具提示
        if self.ad['tooltip']:
            for ui in self._uis:
                ui.setToolTip(self.ad['tooltip'])

        # 颜色设置
        if self.ad['color']:
            fg, bg = self.ad['color']
            readonly = self.ad['readonly']
            if fg:
                fg = QColor(fg.red(), fg.green(), fg.blue(), 
                           fg.alpha() if not readonly else int(fg.alpha() * 0.7))
                style = f"color:rgba({fg.red()}, {fg.green()}, {fg.blue()}, {fg.alpha()});"
                for ui in self._uis:
                    if hasattr(ui, 'setStyleSheet'):
                        ui.setStyleSheet(ui.styleSheet() + style if ui.styleSheet() else style)

    def _add_ui_to_list(self, *uis):
        """将UI元素添加到管理列表"""
        self._uis.extend(uis)

    def _param_value_changed(self):
        """参数值变化时的处理"""
        if self._last_emit_value == self._value:
            return
        self._last_emit_value = self._value
        self.paramChanged.emit(self._name, self._value)

    def paintEvent(self, event):
        """绘制事件"""
        super().paintEvent(event)
        if self._border and hasattr(self._border, 'paint'):
            self._border.paint(self, event)

    def _create_enum_combo(self):
        """创建枚举下拉框（如果支持枚举）"""
        if not self.ad.get('enum'):
            return None
            
        from PyQt6.QtWidgets import QComboBox
        
        mcb = QComboBox()
        if MONO_FONT:
            mcb.setFont(MONO_FONT)
        mcb.addItems([str(it) for it in self.ad['enum']])
        self._rootL.addWidget(mcb)
        self._add_ui_to_list(mcb)
        return mcb

    def _create_range_slider(self, min_val, max_val, step, slider_class):
        """创建范围滑块（如果支持范围）"""
        if not self.ad.get('range') or self.ad.get('enum'):
            return None
            
        start, stop, step = self.ad['range'].start, self.ad['range'].stop, self.ad['range'].step
        start, stop, step = start or min_val, stop, step or step
        
        slider = slider_class(Qt.Orientation.Horizontal, start, stop, step)
        self._rootL.addWidget(slider)
        self._add_ui_to_list(slider)
        return slider