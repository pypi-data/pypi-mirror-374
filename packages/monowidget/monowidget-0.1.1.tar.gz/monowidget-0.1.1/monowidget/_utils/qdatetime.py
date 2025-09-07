"""
美观的日历选择器组件
提供更现代化的日期选择界面
"""

from monowidget._utils.core import *
from PyQt6.QtWidgets import QDateTimeEdit, QVBoxLayout, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import QDate, QDateTime, QTime
from monowidget._utils.qcalendar import QMonoCalendarWidget
from monowidget._utils.qtimeedit import QMonoTimeEdit


class QMonoDateTimeEdit(QWidget):
    """现代化日期时间编辑组件，由QMonoCalendarWidget和QMonoTimeEdit组合而成"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # 创建日期时间编辑框
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        
        # 设置日期时间编辑框样式
        self.datetime_edit.setStyleSheet("""
            QDateTimeEdit {
                padding: 8px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                min-width: 200px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            QDateTimeEdit:focus {
                border-color: #4CAF50;
                outline: none;
                background-color: #f9fff9;
            }
            QDateTimeEdit:hover {
                border-color: #bbb;
            }
            QDateTimeEdit::drop-down {
                border: none;
                width: 30px;
                background-color: transparent;
            }
            QDateTimeEdit::down-arrow {
                image: none;
                border-left: 1px solid #e0e0e0;
                margin-left: 5px;
            }
        """)
        
        # 创建自定义日历
        self.calendar = QMonoCalendarWidget()
        self.datetime_edit.setCalendarWidget(self.calendar)
        
        # 创建时间编辑组件
        self.time_edit = QMonoTimeEdit()
        self.time_edit.set_custom_time_format("HH:mm:ss")
        
        # 创建日期显示标签
        date_label = QLabel("日期:")
        date_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666;
                font-weight: bold;
            }
        """)
        
        # 创建时间显示标签
        time_label = QLabel("时间:")
        time_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #666;
                font-weight: bold;
            }
        """)
        
        # 创建日期时间组合布局
        datetime_layout = QHBoxLayout()
        datetime_layout.addWidget(date_label)
        datetime_layout.addWidget(self.datetime_edit)
        datetime_layout.addWidget(time_label)
        datetime_layout.addWidget(self.time_edit)
        datetime_layout.addStretch()
        
        # 添加到主布局
        main_layout.addLayout(datetime_layout)
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 当时间编辑改变时，同步到日期时间编辑
        self.time_edit.timeChanged.connect(self._sync_time_to_datetime)
        
        # 当日期时间编辑改变时，同步到时间编辑
        self.datetime_edit.dateTimeChanged.connect(self._sync_datetime_to_time)
    
    def _sync_time_to_datetime(self, time):
        """同步时间到日期时间编辑"""
        current_datetime = self.datetime_edit.dateTime()
        new_datetime = QDateTime(current_datetime.date(), time)
        self.datetime_edit.setDateTime(new_datetime)
    
    def _sync_datetime_to_time(self, datetime):
        """同步日期时间到时间编辑"""
        self.time_edit.setTime(datetime.time())
    
    def get_date_time(self):
        """获取当前日期时间"""
        return self.datetime_edit.dateTime()
    
    def set_date_time(self, datetime):
        """设置日期时间"""
        self.datetime_edit.setDateTime(datetime)
        self.time_edit.setTime(datetime.time())
    
    def get_date(self):
        """获取当前日期"""
        return self.datetime_edit.date()
    
    def set_date(self, date):
        """设置日期"""
        current_time = self.time_edit.time()
        new_datetime = QDateTime(date, current_time)
        self.datetime_edit.setDateTime(new_datetime)
    
    def get_time(self):
        """获取当前时间"""
        return self.time_edit.time()
    
    def set_time(self, time):
        """设置时间"""
        self.time_edit.setTime(time)
        current_date = self.datetime_edit.date()
        new_datetime = QDateTime(current_date, time)
        self.datetime_edit.setDateTime(new_datetime)
    
    def set_display_format(self, format_str):
        """设置显示格式"""
        self.datetime_edit.setDisplayFormat(format_str)
    
    def set_date_range(self, min_date, max_date):
        """设置日期范围"""
        self.datetime_edit.setMinimumDate(min_date)
        self.datetime_edit.setMaximumDate(max_date)
        self.calendar.set_minimum_date(min_date)
        self.calendar.set_maximum_date(max_date)
    
    def set_time_range(self, min_time, max_time):
        """设置时间范围"""
        self.time_edit.set_time_range(min_time, max_time)
    
    def set_read_only(self, read_only):
        """设置只读模式"""
        self.datetime_edit.setReadOnly(read_only)
        self.time_edit.set_read_only(read_only)
    
    def is_read_only(self):
        """检查是否为只读模式"""
        return self.datetime_edit.isReadOnly()
    
    def set_enabled(self, enabled):
        """设置启用状态"""
        self.datetime_edit.setEnabled(enabled)
        self.time_edit.setEnabled(enabled)