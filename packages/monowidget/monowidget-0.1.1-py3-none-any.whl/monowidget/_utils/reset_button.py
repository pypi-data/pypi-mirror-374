"""
美观的复位按钮组件
提供统一的样式和符号
"""

from monowidget._utils.core import *
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QFont


class QMonoResetButton(QPushButton):
    """统一的复位按钮组件"""
    
    def __init__(self, parent=None):
        super().__init__("↻", parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置按钮样式"""
        self.setFixedSize(28, 28)  # 从32改为28
        font = QFont()
        font.setPointSize(14)  # 保持字体大小不变
        font.setBold(True)
        self.setFont(font)
        
        # 设置按钮样式和tooltip样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 14px;  /* 从16改为14 */
                color: #495057;
                font-size: 14px;
                font-weight: bold;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #adb5bd;
                color: #212529;
            }
            QPushButton:pressed {
                background-color: #6c757d;
                border-color: #495057;
                color: white;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                border-color: #e9ecef;
                color: #adb5bd;
            }
            QToolTip {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
        """)
        
        self.setToolTip("重置为默认值")
    
    def sizeHint(self):
        """返回推荐大小"""
        return QSize(28, 28)  # 从32改为28