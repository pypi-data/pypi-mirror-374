"""
自定义时间编辑组件
提供现代化的时间输入界面
"""

from monowidget._utils.core import *
from PyQt6.QtWidgets import QTimeEdit
from PyQt6.QtCore import QTime, Qt
from PyQt6.QtGui import QFont


class QMonoTimeEdit(QTimeEdit):
    """现代化时间编辑组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDisplayFormat("HH:mm:ss")
        self.setTime(QTime.currentTime())
        self.setup_styles()
        self.setup_behavior()
    
    def setup_styles(self):
        """设置时间编辑框样式"""
        self.setStyleSheet("""
            QTimeEdit {
                padding: 6px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                min-width: 120px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QTimeEdit:focus {
                border-color: #4CAF50;
                outline: none;
                background-color: #f9fff9;
            }
            QTimeEdit:hover {
                border-color: #bbb;
            }
            QTimeEdit::drop-down {
                border: none;
                width: 25px;
                background-color: transparent;
            }
            QTimeEdit::down-arrow {
                image: none;
                border-left: 1px solid #e0e0e0;
                margin-left: 5px;
            }
            QTimeEdit::up-button, QTimeEdit::down-button {
                width: 20px;
                height: 12px;
                border: none;
                background-color: #f5f5f5;
                border-radius: 3px;
            }
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background-color: #e0e0e0;
            }
            QTimeEdit::up-button:pressed, QTimeEdit::down-button:pressed {
                background-color: #4CAF50;
                color: white;
            }
        """)
    
    def setup_behavior(self):
        """设置时间编辑框行为"""
        # 设置字体
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # 设置对齐方式
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 启用日历弹窗
        self.setCalendarPopup(False)
    
    def set_custom_time_format(self, time_format):
        """设置自定义时间格式"""
        self.setDisplayFormat(time_format)
    
    def get_time(self):
        """获取当前时间"""
        return self.time()
    
    def set_time_range(self, min_time, max_time):
        """设置时间范围"""
        self.setMinimumTime(min_time)
        self.setMaximumTime(max_time)
    
    def set_min_time(self, min_time):
        """设置最小时间"""
        self.setMinimumTime(min_time)
    
    def set_max_time(self, max_time):
        """设置最大时间"""
        self.setMaximumTime(max_time)
    
    def set_read_only(self, read_only):
        """设置只读模式"""
        self.setReadOnly(read_only)
        if read_only:
            self.setStyleSheet(self.styleSheet() + """
                QTimeEdit:read-only {
                    background-color: #f5f5f5;
                    color: #666;
                    border-color: #ddd;
                }
            """)