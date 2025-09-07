from PyQt6.QtWidgets import QDateTimeEdit, QHBoxLayout, QPushButton
from PyQt6.QtCore import QDateTime, pyqtSignal
from .mono_attr_item_base import QMonoAttrItemBase

# 优先从 _utils 导入新的日历组件
try:
    from monowidget._utils import *
    HAS_CUSTOM_CALENDAR = True
except ImportError:
    from PyQt6.QtWidgets import QDateTimeEdit
    HAS_CUSTOM_CALENDAR = False


class QMonoAttrItemDateTime(QMonoAttrItemBase):
    """日期时间类型属性组件"""
    
    def __init__(self, attr_dict, parent=None, *, border=None):
        super().__init__(attr_dict, parent, border=border)
        
    def _create_type_specific_ui(self):
        """创建日期时间类型的UI元素"""
        if HAS_CUSTOM_CALENDAR:
            # 使用美观的自定义日历组件
            self._mwd = QMonoDateTimeEdit()
            self._mwd.datetime_edit.dateTimeChanged.connect(self._datetime_value_changed)
        else:
            # 回退到原有的QDateTimeEdit
            from PyQt6.QtWidgets import QDateTimeEdit
            self._mwd = QDateTimeEdit()
            self._mwd.setCalendarPopup(True)
            self._mwd.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
            self._mwd.setStyleSheet("""
                QDateTimeEdit {
                    padding: 6px 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: white;
                    font-size: 14px;
                    min-width: 180px;
                }
                QDateTimeEdit:focus {
                    border-color: #4CAF50;
                    outline: none;
                }
                QDateTimeEdit::drop-down {
                    border: none;
                    width: 30px;
                }
                QDateTimeEdit::down-arrow {
                    image: none;
                    border-left: 2px solid #e0e0e0;
                    margin-left: 5px;
                }
            """)
            self._mwd.dateTimeChanged.connect(self._datetime_value_changed)
        
        # 设置默认值
        default_value = self.ad['value']
        if isinstance(default_value, str):
            try:
                dt = QDateTime.fromString(default_value, "yyyy-MM-dd HH:mm:ss")
                if not dt.isValid():
                    dt = QDateTime.currentDateTime()
                if HAS_CUSTOM_CALENDAR:
                    self._mwd.set_date_time(dt)
                else:
                    self._mwd.setDateTime(dt)
            except:
                if HAS_CUSTOM_CALENDAR:
                    self._mwd.set_date_time(QDateTime.currentDateTime())
                else:
                    self._mwd.setDateTime(QDateTime.currentDateTime())
        elif hasattr(default_value, 'year'):
            if HAS_CUSTOM_CALENDAR:
                self._mwd.set_date_time(QDateTime(default_value))
            else:
                self._mwd.setDateTime(QDateTime(default_value))
        else:
            if HAS_CUSTOM_CALENDAR:
                self._mwd.set_date_time(QDateTime.currentDateTime())
            else:
                self._mwd.setDateTime(QDateTime.currentDateTime())
            
        # 设置范围限制
        if 'min_datetime' in self.ad:
            min_dt = self._parse_datetime(self.ad['min_datetime'])
            if min_dt and hasattr(self._mwd, 'setMinimumDateTime'):
                self._mwd.setMinimumDateTime(min_dt)
                
        if 'max_datetime' in self.ad:
            max_dt = self._parse_datetime(self.ad['max_datetime'])
            if max_dt and hasattr(self._mwd, 'setMaximumDateTime'):
                self._mwd.setMaximumDateTime(max_dt)
                
        # 将日期时间编辑器插入到标签和复位按钮之间
        self._mainL.insertWidget(1, self._mwd)
        
    def _set_default_value(self, *_, value=None):
        """设置默认值"""
        value = value or self.ad['value']
        self._datetime_value_changed(value, initial=True)
        
    def _datetime_value_changed(self, value, initial=False):
        """日期时间值变化处理"""
        if hasattr(self, '_datetime_vc_flag') and self._datetime_vc_flag:
            return
        self._datetime_vc_flag = True
        
        try:
            if isinstance(value, str):
                dt = QDateTime.fromString(value, "yyyy-MM-dd HH:mm:ss")
                if dt.isValid():
                    if HAS_CUSTOM_CALENDAR:
                        self._mwd.set_date_time(dt)
                    else:
                        self._mwd.setDateTime(dt)
                else:
                    dt = QDateTime.currentDateTime()
                    if HAS_CUSTOM_CALENDAR:
                        self._mwd.set_date_time(dt)
                    else:
                        self._mwd.setDateTime(dt)
            elif hasattr(value, 'year'):  # datetime对象
                dt = QDateTime(value)
                if HAS_CUSTOM_CALENDAR:
                    self._mwd.set_date_time(dt)
                else:
                    self._mwd.setDateTime(dt)
            elif isinstance(value, QDateTime):
                if HAS_CUSTOM_CALENDAR:
                    self._mwd.set_date_time(value)
                else:
                    self._mwd.setDateTime(value)
            else:
                dt = QDateTime.currentDateTime()
                if HAS_CUSTOM_CALENDAR:
                    self._mwd.set_date_time(dt)
                else:
                    self._mwd.setDateTime(dt)
                
            if HAS_CUSTOM_CALENDAR:
                self._value = self._mwd.get_date_time().toPyDateTime()
            else:
                self._value = self._mwd.dateTime().toPyDateTime()
            
        except Exception as e:
            # 出错时使用当前时间
            dt = QDateTime.currentDateTime()
            if HAS_CUSTOM_CALENDAR:
                self._mwd.set_date_time(dt)
                self._value = self._mwd.get_date_time().toPyDateTime()
            else:
                self._mwd.setDateTime(dt)
                self._value = self._mwd.dateTime().toPyDateTime()
            
        self._datetime_vc_flag = False
        
        if not initial:
            self._param_value_changed()
            
    def _parse_datetime(self, dt_str):
        """解析日期时间字符串"""
        if isinstance(dt_str, str):
            dt = QDateTime.fromString(dt_str, "yyyy-MM-dd HH:mm:ss")
            return dt if dt.isValid() else None
        return None
        
    def _get_display_text(self):
        """获取显示文本"""
        if HAS_CUSTOM_CALENDAR:
            return self._mwd.get_date_time().toString("yyyy-MM-dd HH:mm:ss")
        else:
            return self._mwd.dateTime().toString("yyyy-MM-dd HH:mm:ss")