"""
自定义日历组件
提供现代化的日历选择界面
"""

from monowidget._utils.core import *
from PyQt6.QtWidgets import QCalendarWidget
from PyQt6.QtCore import Qt


class QMonoCalendarWidget(QCalendarWidget):
    """现代化日历组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGridVisible(True)
        self.setup_weekday_format()
        self.setup_styles()
    
    def setup_styles(self):
        """设置日历样式 - 改进版本"""
        self.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            
            /* 导航栏月份和年份按钮 - 加宽紧凑版本 */
            QCalendarWidget QToolButton {
                background-color: white;
                border: 1px solid #e0e0e0;
                color: #333;
                font-size: 12px;
                font-weight: bold;
                padding: 4px 12px;
                border-radius: 4px;
                min-width: 80px;
                max-width: 120px;
                min-height: 24px;
                max-height: 24px;
                margin: 1px;
            }
            
            QCalendarWidget QToolButton:hover {
                background-color: #f5f5f5;
                border-color: #ccc;
                min-height: 24px;
                max-height: 24px;
            }
            
            QCalendarWidget QToolButton:pressed {
                background-color: #e8e8e8;
                min-height: 24px;
                max-height: 24px;
            }
            
            QCalendarWidget QToolButton::menu-indicator {
                image: none;
            }
            
            /* 月份导航按钮 - 圆形版本 */
            QCalendarWidget QToolButton#qt_calendar_prevmonth,
            QCalendarWidget QToolButton#qt_calendar_nextmonth,
            QCalendarWidget QToolButton#qt_calendar_prevyear,
            QCalendarWidget QToolButton#qt_calendar_nextyear {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;  /* 圆形：半径=宽高的一半 */
                width: 20px;
                height: 20px;
                font-size: 10px;
                qproperty-icon: none;
                margin: 1px;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
                padding: 0px;
            }
            
            QCalendarWidget QToolButton#qt_calendar_prevmonth {
                qproperty-text: "‹";
            }
            
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                qproperty-text: "›";
            }
            
            QCalendarWidget QToolButton#qt_calendar_prevyear {
                qproperty-text: "«";
            }
            
            QCalendarWidget QToolButton#qt_calendar_nextyear {
                qproperty-text: "»";
            }
            
            QCalendarWidget QToolButton#qt_calendar_prevmonth:hover,
            QCalendarWidget QToolButton#qt_calendar_nextmonth:hover,
            QCalendarWidget QToolButton#qt_calendar_prevyear:hover,
            QCalendarWidget QToolButton#qt_calendar_nextyear:hover {
                background-color: #f5f5f5;
                border-color: #ccc;
                border-radius: 10px;  /* 保持圆形 */
                min-height: 20px;
                max-height: 20px;
            }
            
            QCalendarWidget QToolButton#qt_calendar_prevmonth:pressed,
            QCalendarWidget QToolButton#qt_calendar_nextmonth:pressed,
            QCalendarWidget QToolButton#qt_calendar_prevyear:pressed,
            QCalendarWidget QToolButton#qt_calendar_nextyear:pressed {
                background-color: #e8e8e8;
                border-radius: 10px;  /* 保持圆形 */
                min-height: 20px;
                max-height: 20px;
            }
            
            /* 星期标题 - 去掉'周'字 */
            QCalendarWidget QTableView QHeaderView::section {
                background-color: #f8f8f8;
                color: #666;
                font-size: 12px;
                font-weight: bold;
                padding: 4px;
                border: none;
            }
            
            /* 设置星期标题文本格式 */
            QCalendarWidget QTableView QHeaderView::section:horizontal {
                text-align: center;
            }
            
            /* 日期单元格 */
            QCalendarWidget QTableView {
                alternate-background-color: white;
                selection-background-color: #4CAF50;
                selection-color: white;
                font-size: 12px;
            }
            
            QCalendarWidget QTableView::item {
                padding: 2px;
            }
            
            QCalendarWidget QTableView::item:selected {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
            }
            
            QCalendarWidget QTableView::item:hover {
                background-color: #E8F5E8;
                border-radius: 4px;
            }
            
            /* 当前日期高亮 */
            QCalendarWidget QTableView::item:focus {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
            }
        """)
    
    def set_custom_date_format(self, date_format):
        """设置自定义日期格式"""
        self.setDisplayFormat(date_format)
    
    def get_selected_date(self):
        """获取选中的日期"""
        return self.selectedDate()
    
    def set_minimum_date(self, date):
        """设置最小可选日期"""
        self.setMinimumDate(date)
    
    def set_maximum_date(self, date):
        """设置最大可选日期"""
        self.setMaximumDate(date)
    
    def setup_weekday_format(self):
        """设置星期显示格式，只显示"一"到"日"，去掉周数列"""
        # 设置星期从周一开始
        self.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
        
        # 使用单字母格式显示星期，配合中文环境会显示"一"到"日"
        self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
        
        # 去掉周数列（垂直标题）
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        
        # 设置中文本地化，确保显示为"一"到"日"
        from PyQt6.QtCore import QLocale
        locale = QLocale(QLocale.Language.Chinese, QLocale.Country.China)
        self.setLocale(locale)