from PyQt6.QtWidgets import QWidget

class QMonoWithoutBorder(QWidget):
    """无边框样式的基础类"""
    pass

class QMonoRectBorder(QMonoWithoutBorder):
    """矩形边框样式"""
    pass

class QMonoRoundRectBorder(QMonoWithoutBorder):
    """圆角矩形边框样式"""
    pass