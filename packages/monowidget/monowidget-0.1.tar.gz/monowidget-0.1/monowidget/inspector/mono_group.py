"""
QMonoGroup 类 - 参数分组管理
"""
import os
import sys
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QIcon
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 优先从 _utils 导入
try:
    from monowidget._utils import api_create_triangle_pixel, api_show_layout_widgets, api_hide_layout_widgets
    from monowidget._utils import MONO_HEADER_FONT as MONO_HEADER_FONT
    from monowidget._utils import MONO_TITLE_FONT as MONO_TITLE_FONT
except ImportError:
    # 本地实现
    from .utils import api_create_triangle_pixel, api_show_layout_widgets, api_hide_layout_widgets
    MONO_HEADER_FONT = None
    MONO_TITLE_FONT = None

# 常量定义
GROUP_INDENT = 16
INSPECTOR_SPACE = 4

class QMonoGroup(QWidget):
    def __init__(self, title: str, color: QColor, parent=None):
        super().__init__(parent)
        icon_color = QColor(color.red() // 4, color.green() // 4, color.blue() // 4, color.alpha())
        self.RIGHT_TRIANGLE = api_create_triangle_pixel(16, icon_color, direct="right")
        self.DOWN_TRIANGLE = api_create_triangle_pixel(16, icon_color, direct="down")
        self._color = color
        if not title.endswith(":"): title += ":"
        self._title = title
        self._title_hide = title[:-1]
        self._rootL = QVBoxLayout()
        self._rootL.setContentsMargins(0, 0, 0, 0)
        self._rootL.setSpacing(0)
        self._is_visible = True
        self._title_layout = self._build_title()
        self._setup_header()

        self._mainL = QVBoxLayout()
        self._mainL.setContentsMargins(GROUP_INDENT, 0, 0, 0)
        self._mainL.setSpacing(INSPECTOR_SPACE)

        self._rootL.addLayout(self._mainL)
        self.setLayout(self._rootL)
        self._done_first_paint_flag = False

    @property
    def title(self):
        return self._title

    def _build_title(self):
        _l = QHBoxLayout()
        w = QLabel(self._title)
        if MONO_HEADER_FONT:
            w.setFont(MONO_HEADER_FONT)
        w.setStyleSheet(f"color:rgba({self._color.red()}, {self._color.green()}, {self._color.blue()}, {self._color.alpha()});")
        self._label_widget = w
        _l.addWidget(w)
        _l.addStretch()
        return _l

    def _setup_header(self):
        self.toggle_button = QPushButton()
        self.toggle_button.setFixedSize(20, 20)
        self.toggle_button.setStyleSheet("border: none;")
        self.toggle_button.clicked.connect(self.toggle_visibility)
        self.toggle_button.setIcon(QIcon(self.DOWN_TRIANGLE))
        self.toggle_button.setIconSize(self.toggle_button.size())

        self.title_layout = QHBoxLayout()
        self.title_layout.addWidget(self.toggle_button)
        self.title_layout.addLayout(self._title_layout)
        self.title_layout.addStretch()
        self._rootL.addLayout(self.title_layout)

    def toggle_visibility(self):
        self.setSubVisible(not self._is_visible)

    def setSubVisible(self, visible):
        self._is_visible = visible
        if visible:
            self.toggle_button.setIcon(QIcon(self.DOWN_TRIANGLE))
            api_show_layout_widgets(self._mainL)
            self._label_widget.setText(self._title)
        else:
            self.toggle_button.setIcon(QIcon(self.RIGHT_TRIANGLE))
            api_hide_layout_widgets(self._mainL)
            self._label_widget.setText(self._title_hide)

    @property
    def main_layout(self):
        return self._mainL

    def firstStart(self):
        self.setSubVisible(False)

    def paintEvent(self, a0):
        if not self._done_first_paint_flag:
            self.firstStart()
            self._done_first_paint_flag = True
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._is_visible:
            _color = QColor(self._color.red(), self._color.green(), self._color.blue(), self._color.alpha() // 2)
            painter.setPen(QPen(_color, 1, Qt.PenStyle.DashLine))
            painter.drawLine(10, self._label_widget.height() + 2, 10, self.height() - 2)
        else:
            shd_width, pdelta = 48, 12
            geo = self._label_widget.geometry()
            _color = QColor(self._color.red(), self._color.green(), self._color.blue(), self._color.alpha() // 8)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(_color)
            shd_rect = QRect(geo.right() + 8, geo.top() + 2, shd_width, geo.height() - 4)
            painter.drawRoundedRect(shd_rect, 2, 2)
            _color.setAlpha(_color.alpha() * 4)
            painter.setBrush(_color)
            for i in range(3):
                painter.drawEllipse(QPoint(shd_rect.left() + pdelta * (i + 1), shd_rect.center().y() + 2), 3, 3)