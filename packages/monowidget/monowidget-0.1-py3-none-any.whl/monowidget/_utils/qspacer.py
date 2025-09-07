# -*- coding: utf-8 -*-
from monowidget._utils.core import *

class QMonoSpacer(QWidget):
    def __init__(self, height: int = 20, parent=None):
        super().__init__(parent)
        self.setFixedHeight(height)


class QMonoSeparator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(1)
