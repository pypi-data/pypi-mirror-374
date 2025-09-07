"""
分隔符和间距组件
"""
import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QWidget, QLabel

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 优先从 _utils 导入
try:
    from monowidget._utils import QMonoSeparator, QMonoSpacer, QShadowLabel
except ImportError:
    # 本地实现
    class QMonoSeparator(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedHeight(1)

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            color = QColor("#CCCCCC")
            color.setAlpha(128)
            painter.setPen(QPen(color, 1, Qt.PenStyle.SolidLine))
            painter.drawLine(0, 0, self.width(), 0)

    class QMonoSpacer(QWidget):
        def __init__(self, height=20, parent=None):
            super().__init__(parent)
            self.setFixedHeight(height)

    class QShadowLabel(QLabel):
        def __init__(self, text, color, shadow_color=None, shadow_offset=1, parent=None):
            super().__init__(text, parent)
            self._color = color or QColor("#000000")
            self._shadow_color = shadow_color or QColor("#888888")
            self._shadow_offset = shadow_offset

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 绘制阴影
            painter.setPen(self._shadow_color)
            painter.drawText(self._shadow_offset, self._shadow_offset, 
                            self.width(), self.height(), 
                            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())
            
            # 绘制主文本
            painter.setPen(self._color)
            painter.drawText(0, 0, self.width(), self.height(),
                            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())