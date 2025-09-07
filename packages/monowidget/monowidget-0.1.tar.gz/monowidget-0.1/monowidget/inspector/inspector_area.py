"""
_QMonoInspector_Area 类 - 核心区域管理
"""
import os
import sys
import re
from typing import Dict, Tuple, List
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 优先从 _utils 导入
try:
    from monowidget._utils import MONO_FONT, MONO_HEADER_FONT, MONO_TITLE_FONT, MONO_INSPECTOR_FONT
    from monowidget._utils import QMonoSeparator, QShadowLabel, QMonoSpacer
except ImportError:
    # 本地实现
    from .mono_separator import QMonoSeparator, QShadowLabel, QMonoSpacer
    MONO_FONT = None
    MONO_HEADER_FONT = None
    MONO_TITLE_FONT = None
    MONO_INSPECTOR_FONT = None

from .mono_runtime import MonoaRuntime
from .mono_attr_item import QMonoAttrItem
from .mono_group import QMonoGroup

# 常量
QMONO_TITLE_COLOR = QColor("#000000")
GROUP_INDENT = 16
INSPECTOR_SPACE = 4

class _QMonoInspector_Area(QWidget):
    rebuildTriggered = pyqtSignal(object)

    _vs_widgets: Dict[str, QMonoAttrItem]
    _vs_klass: type
    _vs_inst: object

    def __init__(self, mono_target, parent=None):
        super().__init__(parent)
        self._raw = mono_target.monos
        self.mra = MonoaRuntime()
        self._monos = []
        self._ispts = []

        for m in self._raw:
            mono, ispt = self.mra(m, mono_target.env)
            self._monos.append(mono)
            self._ispts.append(ispt)

        self._mono_widgets = []
        self._group_widgets = {}
        self._current_group: QWidget = None
        self._rootL = QVBoxLayout()
        self._rootL.setContentsMargins(2, 2, 0, 2)
        self._rootL.setSpacing(INSPECTOR_SPACE)
        self.setLayout(self._rootL)

        self._create_ui()
        self.rebuildTriggered.connect(self.rebuild)
        self._on_rebuild_flag = False

        # 初始化 vs
        self._vs_widgets = {}
        self._build_vs()

    def _build_vs(self) -> None:
        """根据当前 _mono_widgets 构造新的动态类"""
        widgets = {w.name: w for w in self._mono_widgets}
        self._vs_widgets = widgets

        cls_name = f"_VS_{id(self):x}"
        ns: Dict[str, object] = {}

        # 为每个 name 创建 property，支持直接访问和修改 widget.value
        for name, w in widgets.items():
            def _make_fget(n: str):
                return lambda self_: self_._vs_widgets[n].value
                
            def _make_fset(n: str):
                return lambda self_, value: setattr(self_._vs_widgets[n], 'value', value)

            ns[name] = property(_make_fget(name), _make_fset(name))

        # 额外暴露 items 属性便于调试
        def _items(self_):
            return {k: v.value for k, v in self_._vs_widgets.items()}

        ns["items"] = property(_items)

        self._vs_klass = type(cls_name, (object,), ns)
        self._vs_inst = self._vs_klass()
        self._vs_inst._vs_widgets = widgets

    @property
    def vs(self):
        """对外只读属性：动态类的实例"""
        return self._vs_inst

    @property
    def rebuild_flag(self):
        return self._on_rebuild_flag

    def rebuild(self, mono_target):
        self._on_rebuild_flag = True
        self._raw = mono_target.monos
        self._monos = []
        self._ispts = []

        for m in self._raw:
            mono, ispt = self.mra(m, mono_target.env)
            self._monos.append(mono)
            self._ispts.append(ispt)

        params_dict = {mono["name"]: mono["value"] for mono in self._monos}
        for qmono in self._mono_widgets:
            if qmono.readonly:
                v = params_dict.get(qmono.name, qmono.value)
                qmono.value = v

        # 重建 UI 后重新生成 vs
        self._build_vs()
        self._on_rebuild_flag = False

    @staticmethod
    def _parse_group_path(group_path: str) -> list:
        return [it.strip() for it in re.split(r"[/\\.]", group_path) if it.strip()]

    def _locate_group(self, group_path: str, color: QColor = None) -> QWidget:
        plst = self._parse_group_path(group_path)
        if not plst:
            self._current_group = None
            return None
        current = self._group_widgets
        self._current_group = None
        for p in plst:
            if p not in current:
                self._set_group(p, color)
                current[p] = [self._current_group, {}]
            self._current_group = current[p][0]
            current = current[p][1]
        return self._current_group

    @property
    def monos(self):
        return self._monos

    def _add_header(self, title: str = "", color: QColor = None, *, font=None, _sys_widget_type=QLabel, _sys_widget_args=()):
        _l = QHBoxLayout()
        w = QMonoSeparator(self)
        _l.addWidget(w)
        w = _sys_widget_type(title + ":" if not title.endswith(":") else title, *_sys_widget_args)
        if font:
            w.setFont(font)
        if color and isinstance(w, QLabel):
            w.setStyleSheet(f"color:rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()});")
        _l.addWidget(w)
        w = QMonoSeparator(self)
        _l.addWidget(w)
        self._add_layout_into(_l)

    def _add_title(self, title: str = "", color: QColor = None):
        return self._add_header(title, color or QColor(0, 0, 0, 200), 
                               font=MONO_TITLE_FONT or None, _sys_widget_type=QShadowLabel,
                               _sys_widget_args=(color or QColor(0, 0, 0, 200), None, 2))

    def _add_separator(self):
        self._add_widget_into(QMonoSeparator(self))

    def _add_space(self, height: int = 20):
        self._add_widget_into(QMonoSpacer(height))

    def _set_group(self, title: str, color: QColor = None):
        if color is None:
            color = QColor(0, 0, 0, 200)
        w = QMonoGroup(title + ":" if not title.endswith(":") else title, color)
        self._add_widget_into(w)
        self._current_group = w

    def _create_inspects(self, isp: list):
        for k, v in isp:
            if k == "group" and v is not None:
                if self._current_group is None or str(v[0]) not in self._current_group.title:
                    self._locate_group(str(v[0]), v[1])
            elif k == "header" and v is not None:
                self._add_header(*v)
            elif k == "title" and v is not None:
                self._add_title(*v)
            elif k == "space" and v is not None:
                self._add_space(v)
            elif k == "separator" and v is True:
                self._add_separator()

    def _create_ui(self):
        for m, isp in zip(self._monos, self._ispts):
            self._create_inspects(isp)
            w = QMonoAttrItem(m)
            self._mono_widgets.append(w)
            self._add_widget_into(w)
        self._rootL.addStretch()

    def _add_widget_into(self, w):
        if self._current_group is None:
            self._rootL.addWidget(w)
        else:
            self._current_group.main_layout.addWidget(w)

    def _add_layout_into(self, l):
        if self._current_group is None:
            self._rootL.addLayout(l)
        else:
            self._current_group.main_layout.addLayout(l)

    @property
    def params(self):
        return {w.name: w.value for w in self._mono_widgets}