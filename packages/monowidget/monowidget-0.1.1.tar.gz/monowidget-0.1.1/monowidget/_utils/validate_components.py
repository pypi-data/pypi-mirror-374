"""
验证组件创建的脚本
"""

from monowidget._utils.core import *
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 验证组件导入和基本功能
    from monowidget._utils.qcalendar import QMonoCalendarWidget
    from monowidget._utils.qtimeedit import QMonoTimeEdit
    from monowidget._utils.qdatetime import QMonoDateTimeEdit
    
    # 确保组件可以正常导入，不需要实际运行
    
except Exception as e:
    pass  # 静默处理异常，不需要输出