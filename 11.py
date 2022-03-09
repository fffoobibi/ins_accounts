import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from ui.demoui import Ui_Form
from components.customwidgets import TitleWidget, TitleBar

TitleWidget.config(
    bar_height=None,
    back_ground_color=None,
    bar_color=Qt.red,
    border_color=Qt.red,
    text_color=Qt.red,
    auto_resize=True,
    nestle_enable=False,
    icon=QIcon(),
    icon_size=16,
    button_text_color=Qt.white,
    button_hover_color=QColor(109, 139, 222),
    button_hide_policy=None
)


class Widget(QWidget, Ui_Form):
    Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)
    CurSorMargins = 2

    def __init__(self):
        super(Widget, self).__init__()

        self._auto_resize = True
        self._pressed = False
        self.nestle_enable = False  # 贴靠
        self.moved = False  # flag
        self.border_color = Qt.lightGray
        self.Direction = None
        self.setMouseTracking(True)

        self.setupUi(self)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self._margins = self.layout().contentsMargins()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setOffset(0)
        shadow.setColor(Qt.black)
        shadow.setBlurRadius(9)

        self.widget.setGraphicsEffect(shadow)
        self.widget.setAutoFillBackground(True)

        palette = self.widget.palette()
        palette.setColor(QPalette.Window, Qt.white)
        self.widget.setPalette(palette)

        self.title_bar = TitleBar()
        self.title_bar.setHeight(28)
        self.title_bar.setBarColor(Qt.lightGray)

        lay = QVBoxLayout(self.widget, spacing=0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.title_bar, 0)
        lay.addWidget(QWidget(), 1)

        self.title_bar.windowMinimumed.connect(self._show_min)
        self.title_bar.windowMaximumed.connect(self._show_max)
        self.title_bar.windowNormaled.connect(self.showNormal)
        self.title_bar.windowClosed.connect(self.close)
        self.title_bar.windowMoved.connect(self.move)
        self.windowTitleChanged.connect(self.title_bar.setTitle)
        self.windowIconChanged.connect(self.title_bar.setIcon)

    def _show_max(self):
        # self.layout().setContentsMargins(0, 0, 0, 0)
        self.showMaximized()

    def _show_min(self):
        # self.layout().setContentsMargins(self._margins)
        self.showMinimized()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._mpos = event.pos()
            self._pressed = True

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        super().mouseReleaseEvent(event)
        self._pressed = False
        self.Direction = None

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super().mouseMoveEvent(event)
        pos = event.pos()
        xPos, yPos = pos.x(), pos.y()
        if self._auto_resize:
            wm, hm = self.width() - self.CurSorMargins, self.height() - self.CurSorMargins
            if self.isMaximized() or self.isFullScreen():
                self.Direction = None
                self.setCursor(Qt.ArrowCursor)
                return
            if event.buttons() == Qt.LeftButton and self._pressed:
                self._resizeWidget(pos)
                return
            if xPos <= self.CurSorMargins and yPos <= self.CurSorMargins:
                # 左上角
                self.Direction = self.LeftTop
                self.setCursor(Qt.SizeFDiagCursor)
            elif wm <= xPos <= self.width() and hm <= yPos <= self.height():
                # 右下角
                self.Direction = self.RightBottom
                self.setCursor(Qt.SizeFDiagCursor)
            elif wm <= xPos and yPos <= self.CurSorMargins:
                # 右上角
                self.Direction = self.RightTop
                self.setCursor(Qt.SizeBDiagCursor)
            elif xPos <= self.CurSorMargins and hm <= yPos:
                # 左下角
                self.Direction = self.LeftBottom
                self.setCursor(Qt.SizeBDiagCursor)
            elif 0 <= xPos <= self.CurSorMargins and self.CurSorMargins <= yPos <= hm:
                # 左边
                self.Direction = self.Left
                self.setCursor(Qt.SizeHorCursor)
            elif wm <= xPos <= self.width() and self.CurSorMargins <= yPos <= hm:
                # 右边
                self.Direction = self.Right
                self.setCursor(Qt.SizeHorCursor)
            elif self.CurSorMargins <= xPos <= wm and 0 <= yPos <= self.CurSorMargins:
                # 上面
                self.Direction = self.Top
                self.setCursor(Qt.SizeVerCursor)
            elif self.CurSorMargins <= xPos <= wm and hm <= yPos <= self.height():
                # 下面
                self.Direction = self.Bottom
                self.setCursor(Qt.SizeVerCursor)

    def _resizeWidget(self, pos):
        """调整窗口大小"""
        if self.Direction == None:
            return
        if not self._auto_resize:
            return
        mpos = pos - self._mpos
        xPos, yPos = mpos.x(), mpos.y()
        geometry = self.geometry()
        x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
        if self.Direction == self.LeftTop:  # 左上角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
        elif self.Direction == self.RightBottom:  # 右下角
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
        elif self.Direction == self.RightTop:  # 右上角
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos.setX(pos.x())
        elif self.Direction == self.LeftBottom:  # 左下角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos.setY(pos.y())
        elif self.Direction == self.Left:  # 左边
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return
        elif self.Direction == self.Right:  # 右边
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            else:
                return
        elif self.Direction == self.Top:  # 上面
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return
        elif self.Direction == self.Bottom:  # 下面
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
            else:
                return
        self.setGeometry(x, y, w, h)

    @property
    def window_size(self) -> QSize:
        return QApplication.desktop().size()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec_())
