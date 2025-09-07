import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QLabel, QApplication
from .inspector_area import _QMonoInspector_Area
from monowidget._utils import *

class QMonoInspector(QWidget):
    paramsChanged = pyqtSignal(dict)
    paramChanged = pyqtSignal(str, object)

    def __init__(self, mono, parent=None):
        super().__init__(parent)
        self._mono = mono
        self._inner = _QMonoInspector_Area(mono)
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setWidget(self._inner)
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._add_mono_title("Mono Inspector:")
        self._layout.addWidget(self._scroll)
        self.setLayout(self._layout)

        for w in self._inner._mono_widgets:
            w.paramChanged.connect(self._any_param_changed)

    def _any_params_changed(self, name: str, value: object):
        if not self._inner.rebuild_flag:
            self.paramsChanged.emit(self.params)

    def _any_param_changed(self, name: str, value: object):
        if not self._inner.rebuild_flag:
            self.paramChanged.emit(name, value)
            self._any_params_changed(name, value)

    def _add_mono_title(self, title: str = "Mono Inspector"):
        logo = QMonoLogo(title, align=Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(logo)

    def rebuildmono(self, s, **params):
        self._mono.handle(s, **params)

    @property
    def rebuildTrigger(self):
        return self._inner.rebuildTriggered

    @property
    def monos(self):
        return self._inner.monos

    @property
    def params(self):
        return self._inner.params

    @property
    def qmonos(self):
        return self._inner._mono_widgets.copy()

    @property
    def vs(self):
        """动态类实例；访问其属性即可实时拿到对应 widget.value"""
        return self._inner.vs

    def closeEvent(self, a0):
        # 可以在这里添加需要的清理逻辑
        super().closeEvent(a0)