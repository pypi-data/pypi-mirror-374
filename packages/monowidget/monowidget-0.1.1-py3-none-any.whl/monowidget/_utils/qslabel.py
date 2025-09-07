# -*- coding: utf-8 -*-
"""
QShadowLabel
    text: str                        显示文本
    color: QColor | None             文字颜色（默认黑色）
    bg_color: QColor | None          背景颜色（None=透明）
    shadow_blur: int                 阴影模糊半径（层数）
    shadow_color: QColor | None      阴影颜色（默认文字颜色 1/4 亮度）
    reversed: bool                   阴影渐变方向（True=内深外淡）
    alignment: Qt.Alignment          文本对齐方式（默认居中）
    parent: QWidget
"""

from monowidget._utils.core import *


class QShadowLabel(QLabel):
    def __init__(
        self,
        text: str,
        color: QColor = None,
        bg_color: QColor = None,
        shadow_blur: int = 3,
        shadow_color: QColor = None,
        reversed: bool = False,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter,
        parent=None,
    ):
        super().__init__(text, parent)

        # 文字颜色
        self._txt_color = color or QColor("black")
        # 背景颜色
        self._bg_color = bg_color
        # 阴影半径/层数
        self._radius = max(0, shadow_blur)
        # 阴影颜色：默认取文字颜色 1/4 亮度
        self._shd_color = shadow_color or QColor(
            self._txt_color.red()   // 4,
            self._txt_color.green() // 4,
            self._txt_color.blue()  // 4,
            self._txt_color.alpha()
        )
        # 渐变方向
        self._reversed = reversed
        # 对齐方式
        self._alignment = alignment

        # 默认字体（可按需再设）
        self.setFont(QFont("Consolas", 12, QFont.Weight.Bold))

    # ------------- 属性访问器 -------------
    # 如需运行时调节，可继续添加 setXxx 接口
    def setShadowColor(self, color: QColor):
        self._shd_color = color
        self.update()

    def setShadowRadius(self, radius: int):
        self._radius = max(0, radius)
        self.update()

    def setReversed(self, rev: bool):
        self._reversed = rev
        self.update()

    # ------------- 绘制 -------------
    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. 背景填充
        if self._bg_color:
            painter.fillRect(self.rect(), self._bg_color)

        # 2. 文字矩形
        rect = self.rect()

        # 3. 逐层绘制阴影
        init_alpha = self._shd_color.alpha()
        color = QColor(self._shd_color.red(), self._shd_color.green(), self._shd_color.blue())

        for i in range(self._radius, -1, -1):
            if self._radius == 0:
                coef = 1.0
            else:
                coef = (i / self._radius) if not self._reversed else (1 - i / self._radius)
            color.setAlpha(int(init_alpha * coef + 0.5))
            painter.setPen(color)
            painter.setFont(self.font())
            painter.drawText(
                rect.adjusted(i, i, i, i),  # 偏移
                self._alignment,
                self.text()
            )

        # 4. 绘制前景文字
        painter.setPen(QPen(self._txt_color))
        painter.setFont(self.font())
        painter.drawText(rect, self._alignment, self.text())
        
        
        
class QMonoLogo(QWidget):
    """
    水平 Logo，默认文字 “Mono Widget”。
    align 只控制整体在控件内的左 / 中 / 右排布。
    """
    def __init__(
        self,
        logo_str: str = "Mono Widget",
        parent=None,
        align=Qt.AlignmentFlag.AlignCenter,
        shadow_blur: int = 2,                  # 新增：阴影半径
        shadow_color: QColor = None,           # 新增：阴影颜色
        reversed_shadow: bool = False,         # 新增：渐变方向
    ):
        super().__init__(parent)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._add_mono_title(
            logo_str,
            align,
            shadow_blur=shadow_blur,
            shadow_color=shadow_color,
            reversed_shadow=reversed_shadow,
        )

    # 抽出来方便复用
    def _add_mono_title(
        self,
        title: str,
        align: Qt.AlignmentFlag,
        shadow_blur: int,
        shadow_color: QColor,
        reversed_shadow: bool,
    ):
        inner = QHBoxLayout()
        
        # 左对齐：不添加stretch，直接添加标签
        if align == Qt.AlignmentFlag.AlignLeft:
            pass
        elif align == Qt.AlignmentFlag.AlignCenter:
            inner.addStretch()
        elif align == Qt.AlignmentFlag.AlignRight:
            inner.addStretch()

        # 用新版 QShadowLabel
        label = QShadowLabel(
            text=title,
            color=QMONO_TITLE_COLOR,     # 文字颜色
            bg_color=None,               # 背景透明
            shadow_blur=shadow_blur,     # 阴影半径
            shadow_color=shadow_color,   # 阴影颜色（None 则用默认）
            reversed=reversed_shadow,    # 方向
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        label.setFont(MONO_INSPECTOR_FONT)

        inner.addWidget(label)
        
        # 右对齐或居中对齐时添加stretch
        if align == Qt.AlignmentFlag.AlignCenter:
            inner.addStretch()
        elif align == Qt.AlignmentFlag.AlignRight:
            inner.addStretch()

        self._layout.addLayout(inner)