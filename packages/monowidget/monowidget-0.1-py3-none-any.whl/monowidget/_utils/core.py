# -*- coding: utf-8 -*-
import sys
import re
import types
import warnings
from rbpop import *
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional, Union
from monowidget._utils.const import *
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
                             QDoubleSpinBox, QLineEdit, QCheckBox, QComboBox,
                             QPushButton, QApplication, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QPropertyAnimation, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QBrush, QPixmap, QIcon

warnings.filterwarnings("ignore", category=DeprecationWarning)


#region Monoa
class MonoaRuntimeEvalError(Exception):
    def __init__(self, monoa, msg):
        txt = f"\n\t{str(msg)}\n\n\tLineno:{monoa.lineno}, Target:\n\t\t{monoa}"
        super().__init__(txt)

class MonoaRuntimeUnexpectedColor(MonoaRuntimeEvalError): pass


class MonoaRuntimeDismatchedEnumType(MonoaRuntimeEvalError): pass


class MonoaRuntimeDismatchedRangeType(MonoaRuntimeEvalError): pass


def find_value_enum_closest(value: float, enum_list: List[Any]) -> Tuple[int, Any]:
    """找到最接近 value 的枚举值及其索引。"""
    if not enum_list:
        return -1, value
    closest_value = min(enum_list, key=lambda x: abs(float(x) - value))
    return enum_list.index(closest_value), closest_value


def str_crop(s, size=200):
    s = str(s)
    if len(s) > size:
        return s[:size] + '...'


def api_hide_layout_widgets(layout):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()
        if widget:
            widget.hide()
        else:
            if item.layout():
                api_hide_layout_widgets(item.layout())


def api_show_layout_widgets(layout):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()
        if widget:
            widget.show()
        else:
            if item.layout():
                api_show_layout_widgets(item.layout())


def api_create_triangle_pixel(size: int, color: QColor = QColor("black"), direct="down"):
    assert direct in ["down", "right"], "direct must be 'down' or 'right'"
    pm = QPixmap(size, size)
    pm.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(color)
    if direct == "down":
        points = [QPoint(0, 0), QPoint(size, 0), QPoint(size // 2, size)]
    else:
        points = [QPoint(0, 0), QPoint(0, size), QPoint(size, size // 2)]
    painter.drawPolygon(*points)
    painter.end()
    return pm


def api_merge_colors(*qc):
    red_sum, green_sum, blue_sum, alpha_sum = 0, 0, 0, 0
    count = 0
    for color in qc:
        weight, color = (color[0], color[1]) if isinstance(color, tuple) else (1, color)
        red_sum += color.red() * weight
        green_sum += color.green() * weight
        blue_sum += color.blue() * weight
        alpha_sum += color.alpha() * weight
        count += weight
    if count > 0:
        return QColor(red_sum // count, green_sum // count, blue_sum // count, alpha_sum // count)
    return QColor(0, 0, 0, 0)


#endregion


