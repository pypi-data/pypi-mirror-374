# -*- coding: utf-8 -*-
from monowidget._utils.core import *
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QFrame


class _QMonoSlider(QFrame):
    monoChanged: pyqtSignal = None

    @abstractmethod
    def __init__(self, orientation:Qt.Orientation, min_val: any, max_val:any, step:any=1, parent=None):
        super().__init__(parent)
        pass

    @abstractmethod
    def setValue(self, value) -> None:
        pass

    @abstractmethod
    def value(self, value) -> any:
        pass


class QIntSlider(_QMonoSlider):
    monoChanged = pyqtSignal(int)

    def __init__(self, orientation, min_val: int, max_val: int, step: int = 1, parent=None):
        super().__init__(orientation, min_val, max_val, step, parent)
        self._min = min_val
        self._max = max_val
        self._step = step
        self._value = min_val
        self.setMinimumHeight(30)
        self.setMouseTracking(True)
        self._dragging = False

    def setValue(self, value: int):
        if self._min <= value <= self._max:
            self._value = value
            self.monoChanged.emit(value)
            self.update()  # Trigger paintEvent

    def value(self) -> int:
        return self._value

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._update_value_from_pos(event.position())
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._update_value_from_pos(event.position())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()

    def _update_value_from_pos(self, pos):
        rect = self.rect().adjusted(5, 5, -5, -5)
        ratio = max(0, min(1, (pos.x() - rect.x()) / rect.width()))
        value = self._min + ratio * (self._max - self._min)
        value = round(value / self._step) * self._step
        self.setValue(int(value))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Plain style - no background, just groove and handle
        rect = self.rect().adjusted(5, 5, -5, -5)
        
        # Draw groove only
        groove_rect = QRectF(rect.x(), rect.center().y() - 2, rect.width(), 4)
        painter.setBrush(QColor(220, 220, 220))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(groove_rect, 2, 2)
        
        # Draw handle
        ratio = (self._value - self._min) / (self._max - self._min)
        handle_x = rect.x() + ratio * rect.width()
        handle_rect = QRectF(handle_x - 6, rect.center().y() - 6, 12, 12)
        painter.setBrush(QColor(66, 133, 244))  # Google blue
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(handle_rect)

class QDoubleSlider(_QMonoSlider):
    monoChanged = pyqtSignal(float)

    def __init__(self, orientation, min_val: float, max_val: float, step: float = 0.1, parent=None):
        super().__init__(orientation, min_val, max_val, step, parent)
        self._min = min_val
        self._max = max_val
        self._step = step
        self._value = min_val
        self.setMinimumHeight(30)
        self.setMouseTracking(True)
        self._dragging = False

    def setValue(self, value: float):
        if self._min <= value <= self._max:
            self._value = value
            self.monoChanged.emit(value)
            self.update()  # Trigger paintEvent

    def value(self) -> float:
        return self._value

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._update_value_from_pos(event.position())
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging:
            self._update_value_from_pos(event.position())
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()

    def _update_value_from_pos(self, pos):
        rect = self.rect().adjusted(5, 5, -5, -5)
        ratio = max(0, min(1, (pos.x() - rect.x()) / rect.width()))
        value = self._min + ratio * (self._max - self._min)
        value = round(value / self._step) * self._step
        self.setValue(float(value))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Plain style - no background, just groove and handle
        rect = self.rect().adjusted(5, 5, -5, -5)
        
        # Draw groove only
        groove_rect = QRectF(rect.x(), rect.center().y() - 2, rect.width(), 4)
        painter.setBrush(QColor(220, 220, 220))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(groove_rect, 2, 2)
        
        # Draw handle
        ratio = (self._value - self._min) / (self._max - self._min)
        handle_x = rect.x() + ratio * rect.width()
        handle_rect = QRectF(handle_x - 6, rect.center().y() - 6, 12, 12)
        painter.setBrush(QColor(66, 133, 244))  # Google blue
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(handle_rect)
