"""
Inspector 工具函数
"""
import os
import sys
from PyQt6.QtGui import QColor, QPixmap, QPainter
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QWidget, QLayout

# 添加项目根目录到路径，以便导入 _utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 从 _utils 导入所需函数和类
try:
    from monowidget._utils import api_create_triangle_pixel, api_show_layout_widgets, api_hide_layout_widgets
except ImportError:
    # 如果 _utils 中没有这些函数，提供实现
    def api_create_triangle_pixel(size, color, direct="right"):
        """创建三角形像素图"""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        if direct == "right":
            points = [QPoint(2, 2), QPoint(size-2, size//2), QPoint(2, size-2)]
        elif direct == "down":
            points = [QPoint(2, 2), QPoint(size//2, size-2), QPoint(size-2, 2)]
        else:
            points = [QPoint(2, 2), QPoint(size-2, 2), QPoint(size//2, size-2)]
        
        painter.drawPolygon(*points)
        painter.end()
        return pixmap

    def api_show_layout_widgets(layout):
        """显示布局中的所有控件"""
        if layout is not None:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget():
                    item.widget().show()
                elif item.layout():
                    api_show_layout_widgets(item.layout())

    def api_hide_layout_widgets(layout):
        """隐藏布局中的所有控件"""
        if layout is not None:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget():
                    item.widget().hide()
                elif item.layout():
                    api_hide_layout_widgets(item.layout())

def _default_color(FG_COLOR, FG_ALPHA, BG_COLOR, BG_ALPHA) -> tuple:
    """处理颜色"""
    fg = QColor(FG_COLOR)
    if FG_COLOR:
        fg.setAlpha(FG_ALPHA)
    else:
        fg = None
        
    bg = QColor(BG_COLOR) if BG_COLOR else None
    if bg:
        bg.setAlpha(BG_ALPHA)
    else:
        bg = None
        
    if fg is None and bg is None:
        return None
    return (fg, bg)

def _api_prehandle_single_attr(attr: str):
    """处理属性字符串"""
    attr = attr.strip()
    return attr if attr.endswith(')') else attr + '()'