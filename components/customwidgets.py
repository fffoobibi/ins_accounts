# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 16:17
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : customwidgets.py
# @Software: PyCharm
import re
import sys
import time
import math
import asyncio
import aiohttp
import threading

from enum import IntEnum
from collections import deque
from datetime import datetime
from datetime import timedelta as dt
from enum import Enum

from pathlib import Path
from types import MethodType
from typing import Coroutine, Type
from inspect import isgenerator

from typing_extensions import Literal
from typing import Optional, Generator, Tuple, Any, Union, List, Callable

from PyQt5.QtWidgets import (QApplication, QLineEdit, QPushButton, QLabel, QWidget, QDialog, QFileDialog,
                             QListWidgetItem, QFrame, QStyledItemDelegate, QStyleOptionViewItem, QComboBox,
                             QCompleter, QListWidget, QListView, QGridLayout, QSpacerItem, QSizePolicy, QHBoxLayout,
                             QVBoxLayout, QTableWidget, QHeaderView, QMenu)
from PyQt5.QtCore import (QObject, QThread, QRectF, QModelIndex, QSortFilterProxyModel, QSettings,
                          Qt, pyqtSignal, QSize, QPropertyAnimation, QMargins,
                          pyqtSlot, QByteArray, QBuffer, QEvent, QRect, QPoint)
from PyQt5.QtGui import (QPixmap, QIcon, QCursor, QKeyEvent, QMovie, QPainter, QTransform,
                         QColor, QFont, QEnterEvent, QPalette, QPen, QFontMetrics, QWheelEvent,
                         QMouseEvent, QResizeEvent, QKeySequence, QPainterPath, QPolygonF, QBitmap)

from .styles import Sh


class BindSettings(dict):
    _bind_fiels_ = {}

    def bind_field(
            self,
            key: str,
            target: QWidget,
            read_func: str = "text",
            set_func: str = "setText",
    ):
        self._bind_fiels_[key] = (target, read_func, set_func)

    def __getattr__(self, key):
        if key in self._bind_fiels_:
            target, read_func, _ = self._bind_fiels_.get(key)
            self[key] = getattr(target, read_func)()
            return self[key]

    def __setattr__(self, key: str, value: str) -> None:
        self[key] = value
        if key in self._bind_fiels_:
            print(self._bind_fiels_.get(key))
            target, _, set_func = self._bind_fiels_.get(key)
            try:
                getattr(target, set_func)(value)
            except:
                pass


class ValidateLine(QLineEdit):
    validate_fail = pyqtSignal()
    validate_success = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_validator = None
        self.required = True
        self.validate_flag = False
        self._validators = []

    def validate_(self) -> Tuple[bool, str]:
        for val, _ in self._validators:
            flag, msg = val(self.text())
            if not flag:
                return False, msg
        return True, '验证通过'

    def validate(self, text: str = None) -> bool:
        self.validate_flag = True
        t = text or self.text().strip()
        if self.required:
            if not t:
                self.validate_fail.emit()
                return False
        if self.custom_validator:
            if self.custom_validator.search(t) is None:
                self.validate_fail.emit()
                return False
            else:
                self.validate_success.emit()
                return True
        self.validate_flag = False
        return True

    def setCustomValidator(self, pattern: Union[str, Callable], msg: str = ''):
        if isinstance(pattern, str):
            self._validators.append([pattern, msg])
            self.custom_validator = lambda v: re.compile(
                pattern, re.IGNORECASE).search(v)
        else:
            self._validators.append([pattern, msg])
            self.custom_validator = pattern


# 这个类是解决 global 关键字不太好使的问题
class Setter:
    def __init__(self, initialValue=None) -> None:
        self._value = initialValue
        self._result = None

    def get(self):
        return self._value

    def set(self, v):
        self._value = v

    def result(self, v):
        self._result = v


class Result():
    def __init__(self, task):
        self.task = task

    def get(self):
        return self.task._result


# 防抖装饰器
def debounce(delay):
    # 用于存储 asyncio.Task 实例，这里是闭包
    task = Setter()

    def decorator(fn):
        # Task 协程函数
        async def f(*args, **kwargs):
            # 进行休眠
            await asyncio.sleep(delay)

            # 调用函数
            f1 = fn(*args, **kwargs)

            # 支持回调函数是异步函数的情况
            if asyncio.iscoroutine(f1):
                res = await f1
                task.result(res)
            else:
                task.result(f1)

            # 清除 task
            task.set(None)

        def wrapper(*args, **kwargs):
            # 如果 task 存在，说明在 delay 秒内调用过一次函数，此次调用应当重置计时器，因此取消先前的 Task
            if task.get() is not None:
                task.get().cancel()

            # 创建 Task 并赋值变量 task
            aio = asyncio.create_task(f(*args, *kwargs))
            task.set(aio)

            return Result(task)

        return wrapper

    return decorator


# 节流装饰器，节流比较简单，也不需要用到异步特性
def throttle(delay):
    # 下一次许可调用的时间，初始化为 0
    next_t = Setter(0)

    def decorator(fn):
        def wrapper(*args, **kwargs):
            # 当前时间
            now = time.time()

            # 若未到下一次许可调用的时间，直接返回
            if next_t.get() > now:
                return

            # 更新下一次许可调用的时间
            next_t.set(now + delay)

            # 调用函数并返回
            return fn(*args, **kwargs)

        return wrapper

    return decorator


class ValidateLineEx(ValidateLine):
    def __init__(self, *a, **kw):
        super(ValidateLineEx, self).__init__(*a, **kw)

    def set_place_holder(self, text):
        self.setPlaceholderText(text)

    def validate(self, msg: str = None, show=False) -> bool:
        for pattern, msg in self._validators:
            if isinstance(pattern, str):
                pat = re.compile(pattern).search(self.text())
            else:
                pat = pattern(self.text())
            flag, m = pat
            if not flag:
                if show:
                    v = Toast.make_text(msg, self, keep=False)
                    try:
                        v.setFocusPolicy(Qt.NoFocus)
                        self.setFocus(Qt.MouseFocusReason)
                    except:
                        import traceback
                        traceback.print_exc()
                return False
        return True

    def validate_(self) -> Tuple[bool, str]:
        for val, _ in self._validators:
            flag, msg = val(self.text())
            if not flag:
                return False, msg
        return True, '验证通过'


class ValidateLineEx2(QWidget):
    def __init__(self, *a, **kw):
        super(ValidateLineEx2, self).__init__(*a, **kw)
        lay = QGridLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.line = ValidateLine()
        lay.addWidget(0, 0, self.line)
        self.text_label = QLabel()
        self.text_label.setStyleSheet(
            'border:none;color: red;background: transparent;font-family: 微软雅黑;font-size:9pt')
        lay.addWidget(1, 0, self.text_label)

    def __getattr__(self, item):
        return getattr(self.line, item)

    def setText(self, txt):
        self.line.setText(txt)

    def setValidator(self, p: Union[Callable[[str], Tuple[bool, str]], str], msg=''):
        self.line.setCustomValidator(p, msg)

    def validate_(self) -> bool:
        for val, _ in self.line._validators:
            flag, msg = val(self.text())
            if not flag:
                self.text_label.setText(msg)
                return False
        return True


class ComboLine(ValidateLine):
    add_sig = pyqtSignal(str)
    pop_sig = pyqtSignal(str)
    search_flag = pyqtSignal()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.textEdited.connect(self.pop_sig)
        self.textEdited.connect(lambda v: self.search_flag.emit())
        self.setClearButtonEnabled(False)

    def focusOutEvent(self, a0) -> None:
        super(ComboLine, self).focusOutEvent(a0)
        if self.text().strip():
            self.add_sig.emit(self.text())


class SearchComBo(QComboBox):
    search_sig = pyqtSignal(list)

    def __init__(self, *a, **kw):
        super(SearchComBo, self).__init__(*a, **kw)
        self.setEditable(True)
        self.setLineEdit(ComboLine())
        self.setMaxVisibleItems(10)
        self.setView(QListView())
        self.log_list = deque()

        # 添加筛选器模型来筛选匹配项
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(
            Qt.CaseInsensitive)  # 大小写不敏感
        self.pFilterModel.setSourceModel(self.model())

        # 添加一个使用筛选器模型的QCompleter
        self.completer = QCompleter(self.pFilterModel, self)
        # 始终显示所有(过滤后的)补全结果
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)  # 不区分大小写
        popup_view = QListView()
        popup_view.setStyleSheet(Sh.historycombobox_listview_style)
        popup_view.verticalScrollBar().setStyleSheet(Sh.history_v_scroll_style)
        self.completer.setPopup(popup_view)
        self.setCompleter(self.completer)

        # Qcombobox编辑栏文本变化时对应的槽函数
        self.lineEdit().textEdited.connect(self._text_changed)
        self.lineEdit().add_sig.connect(self._detect)
        self.completer.activated.connect(self.on_completer_activated)
        self.lineEdit().setClearButtonEnabled(False)

    def focusOutEvent(self, e) -> None:
        super().focusOutEvent(e)
        self.set_normal_style()

    def set_normal_style(self):
        self.setStyleSheet('''
              QComboBox {
              border:2px solid #ADC3F4;
              border-radius: 3px;
              height:26px;
              background:white;
              font-family: 微软雅黑;
              padding-left: 1px;}
              QComboBox:focus{
              border: 2px solid rgb(122,161,245)}
              QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
              }
              QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/箭头 下(1).svg')}
              QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}
              ''')

    def set_search_style(self):
        self.setStyleSheet('''
        QComboBox {
        border:2px solid #ADC3F4;
        border-radius: 3px;
        height:26px;
        background:white;
        font-family: 微软雅黑;
        padding-left: 1px;}
        QComboBox:focus{
        border: 2px solid rgb(122,161,245)}
        QComboBox::drop-down{subcontrol-origin: padding;subcontrol-position: center right;width:30px;height:36px;border-left: none;
        }
        QComboBox::down-arrow{width:  17px;height: 17px;image: url(':/imgs/搜索小.svg')}
        QComboBox::down-arrow:on{width:  17px;height: 17px;image: url(':/imgs/箭头 右(1).svg')}''')

    def _text_changed(self, value):
        self.pFilterModel.setFilterFixedString(value)
        if value:
            self.set_search_style()
        else:
            self.set_normal_style()

    def item_texts(self):
        return [self.itemText(i) for i in range(self.count())]

    @pyqtSlot(str)
    def _detect(self, value):
        if value not in self.item_texts():
            self.lineEdit().clear()

    # 当在Qcompleter列表选中候，下拉框项目列表选择相应的子项目
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.set_search_style()
            # self.activated[str].emit(self.itemText(index))

    # 在模型更改时，更新过滤器和补全器的模型
    def setModel(self, model):
        super(SearchComBo, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # 在模型列更改时，更新过滤器和补全器的模型列
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(SearchComBo, self).setModelColumn(column)

    # 回应回车按钮事件
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Enter & e.key() == Qt.Key_Return:
            text = self.currentText()
            # Qt.MatchExactly |
            index = self.findText(
                text, Qt.MatchCaseSensitive | Qt.MatchContains)
            if index > -1:
                self.setCurrentIndex(index)
            self.hidePopup()
            if index > -1:
                super(SearchComBo, self).keyPressEvent(e)
        else:
            super(SearchComBo, self).keyPressEvent(e)

    def current_data(self, user_role=Qt.UserRole):
        index = self.currentIndex()
        return self.itemData(index, user_role)

    def item_datas(self) -> List[Tuple[str, Any]]:
        res = []
        for i in range(self.count()):
            text, value = self.itemText(i), self.itemData(i, Qt.UserRole)
            res.append([text, value])
        return res

    def save_logs(self, file: QSettings, key='basic/historys'):
        dq = deque(maxlen=10)
        dq.extend(self.item_datas())
        file.setValue(key, list(dq))

    def add_datas(self, values):
        for text, value in values:
            self.addItem(text, value)

    @debounce(1)
    async def search(self):
        url = 'http://192.168.0.10:8041/account/getAccountList'
        data = {
            'account_name': self.currentText()
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                js_data = await resp.json()
                if js_data.get('code') == 0:
                    datas = js_data.get('response').get('list')
                    datas = [(d.get('id'), d.get('account_name'))
                             for d in datas]
                    self.search_sig.emit(datas)
                    return datas
                raise Exception('not found accounts')


class SeachComBoEx(SearchComBo):

    def __init__(self, *a, **kw):
        super(SeachComBoEx, self).__init__(*a, **kw)
        self.lineEdit().setClearButtonEnabled(False)

    def set_place_holder(self, text: str):
        self.lineEdit().setPlaceholderText(text)

    def set_search_style(self):
        pass

    def set_normal_style(self):
        pass

    def add_datas(self, values: List[Tuple[str, Any]]):
        super(SeachComBoEx, self).add_datas(values)

    def set_current_index_by_data(self, value):
        index = -1
        for i in range(self.count()):
            data = self.itemData(i, Qt.UserRole)
            if str(data) == str(value):
                index = i
                break
        if index > -1:
            self.setCurrentIndex(index)


class LoadListWidget(QListWidget):
    load_more_sig = pyqtSignal()
    loading_state = pyqtSignal()
    clear_signal = pyqtSignal()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.verticalScrollBar().actionTriggered.connect(self._load)
        self.wheel_up = None
        self.loading_index = None
        self.wait_loading = False
        self.load_flag = True
        self.loading_condition: Callable = None

        self._global_loading = GifLabel(self)
        self._global_loading.setStyleSheet(
            'border:none;background-color:transparent')
        fm = self._global_loading.fontMetrics().height()
        self._global_loading.setFixedSize(QSize(40, fm * 2))
        self._global_loading.hide()

        self._no_data = QWidget(self)
        label = QLabel()
        label.setScaledContents(True)
        label.setPixmap(QPixmap(':/imgs/缺省页_暂无数据.svg'))
        h = 60
        label.setFixedSize(QSize(h, h))
        label2 = QLabel('暂无数据')
        label2.setStyleSheet('border:none;color:gray;font-family:微软雅黑')
        hei = label2.fontMetrics().height() * 1.5
        label2.setFixedHeight(hei)
        label2.setAlignment(Qt.AlignCenter)
        lay = QVBoxLayout(self._no_data)
        lay.setSpacing(1)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.addWidget(label)
        lay.addWidget(label2)
        self._no_data.setFixedSize(QSize(h + 4, h + 5 + hei))
        self._no_data.hide()

    def clear(self):
        super().clear()
        self.clear_signal.emit()

    def add_widget(self, widget: QWidget, item_size: QSize, search_text: str = None):
        def bind():
            widget.raw_alive = False

        if search_text is not None:
            item = self.search_item(search_text)
        else:
            item = QListWidgetItem()
        item.setSizeHint(item_size)
        self.addItem(item)
        self.setItemWidget(item, widget)
        self.clear_signal.connect(bind)

    def find_widget(self, tag: str):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            if widget is not None:
                if widget.tag().strip() == tag.strip():
                    return widget

    def search(self, text: str):
        if text == '':
            for it in range(self.count()):
                item = self.item(it)
                item.setHidden(False)
        else:
            items = self.findItems(text, Qt.MatchContains)
            for it in range(self.count()):
                item = self.item(it)
                if item not in items:
                    item.setHidden(True)
                else:
                    item.setHidden(False)

    def search_item(self, text: str) -> QListWidgetItem:
        item = QListWidgetItem()
        item.setText(text)
        item.setForeground(Qt.transparent)
        return item

    def set_loding_condition(self, func: Callable):
        self.loading_condition = func

    def set_loading_enable(self, flag: bool):
        self.load_flag = flag

    def show_global_loading(self):
        self.load_flag = False
        w, h = self.width(), self.height()
        gw, gh = self._global_loading.width(), self._global_loading.height()
        sw = int((w - gw) / 2)
        sh = int((h - gh) / 2)
        self._global_loading.move(sw, sh)
        self._global_loading.show()
        self._global_loading.raise_()
        self._global_loading.setGif(':/imgs/加载2.gif')
        self.setEnabled(False)

    def hide_global_loading(self):
        self.load_flag = True
        self._global_loading.removeGif('')
        self._global_loading.hide()
        self.setEnabled(True)

    def show_no_data(self):
        self.load_flag = False
        w, h = self.width(), self.height()
        gw, gh = self._no_data.width(), self._no_data.height()
        sw = int((w - gw) / 2)
        sh = int((h - gh) / 2)
        self._no_data.move(sw, sh)
        self._no_data.show()
        self._no_data.raise_()

    def hide_no_data(self):
        self.load_flag = True
        self._no_data.hide()

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        if not self._global_loading.isHidden():
            w, h = self.width(), self.height()
            gw, gh = self._global_loading.width(), self._global_loading.height()
            sw = int((w - gw) / 2)
            sh = int((h - gh) / 2)
            self._global_loading.move(sw, sh)
        if not self._no_data.isHidden():
            w, h = self.width(), self.height()
            gw, gh = self._no_data.width(), self._no_data.height()
            sw = int((w - gw) / 2)
            sh = int((h - gh) / 2)
            self._no_data.move(sw, sh)

    def start_loading(self):
        if self.load_flag:
            condition = self.loading_condition() if self.loading_condition is not None else True
            if condition:
                self.loading_index = self.count()
                self.wait_loading = True
                self.hide_no_data()
                self.hide_global_loading()
                item = QListWidgetItem(self)
                item.setSizeHint(QSize(100, 30))
                item.setBackground(Qt.gray)
                widget = QWidget()
                widget.setFixedHeight(30)
                btn = GifButton()
                btn.setText('加载中')
                btn.setStyleSheet('border:none;font-family:微软雅黑')
                btn.setGif(':/imgs/加载2.gif')
                lay = QHBoxLayout(widget)
                lay.addWidget(btn)
                widget.setStyleSheet('background-color: transparent')
                self.setItemWidget(item, widget)
                self.load_more_sig.emit()

    def end_loading(self):
        if self.loading_index is not None:
            if self.wait_loading:
                self.hide_global_loading()
                self.hide_no_data()
                item = self.takeItem(self.loading_index)
                self.removeItemWidget(item)
                self.loading_index = None
                self.wait_loading = False

    def cant_loading(self):
        item = QListWidgetItem()
        item.setForeground(Qt.gray)
        item.setSizeHint(QSize(100, 30))
        label = QLabel()
        label.setFont(QFont('微软雅黑'))
        label.setText('一一一 到底了 一一一')
        label.setStyleSheet(
            'border:none;background-color:transparent;color:gray')
        label.setAlignment(Qt.AlignCenter)
        self.addItem(item)
        self.setItemWidget(item, label)

    def _max(self):
        return self.verticalScrollBar().maximum()

    def _load(self, v):
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            if not self.wait_loading:
                self.start_loading()

    def wheelEvent(self, e: QWheelEvent) -> None:
        super().wheelEvent(e)
        if e.angleDelta().y() < 0:
            self.wheel_up = True
        else:
            self.wheel_up = False


class UploadListWidget(QListWidget):
    file_size_max = pyqtSignal(str)
    file_changed = pyqtSignal()
    preview_signal = pyqtSignal(QListWidgetItem)
    _signal = pyqtSignal()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._max_files = 5
        self._max_file_size = 1024 * 1024 * 2  # 默认2mb
        self.min_height = kw.pop('min_height', 90)
        self.upload_img = kw.pop('upload_img', ':/imgs/添加.svg')
        self.forbib_img = kw.pop('forbid_img', ':/imgs/禁止.svg')
        self.widget_size = kw.pop('widget_size', 80)
        self.file_changed.connect(self._signal)
        self.add_widget: QWidget = None

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSpacing(3)
        self.setStyleSheet(Sh.upload_list_page_style)
        self.horizontalScrollBar().setStyleSheet(Sh.upload_scroll_style)
        self._add_upload_state()
        self.setMinimumHeight(self.min_height)
        self.setMaximumHeight(self.min_height)

        btn_style = 'border:none;background-color: transparent'
        btn_size = QSize(18, 18)

        self.pre_btn = QPushButton(self)
        self.nex_btn = QPushButton(self)
        # self.pre_btn.setCursor(Qt.PointingHandCursor)
        # self.nex_btn.setCursor(Qt.PointingHandCursor)

        self.pre_btn.setFixedSize(btn_size)
        self.nex_btn.setFixedSize(btn_size)

        self.pre_btn.setIcon(QIcon(':/imgs/后退面性.svg'))
        self.nex_btn.setIcon(QIcon(':/imgs/前进面性.svg'))

        self.pre_btn.setStyleSheet(btn_style)
        self.nex_btn.setStyleSheet(btn_style)

        self.pre_btn.hide()
        self.nex_btn.hide()

        self._signal.connect(self._show_btns)

    def _show_btns(self):
        if self.add_widget is not None:
            count = self.current_file_count
            h = self.widget_size * (count + 1) + count * self.spacing()
            if h >= self.width():
                self.nex_btn.raise_()
                self.pre_btn.raise_()
                self.nex_btn.show()
                self.pre_btn.show()
            else:
                self.nex_btn.hide()
                self.pre_btn.hide()

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        w, h = self.width(), self.height()
        hh = int((h - 18) / 2)
        self.pre_btn.move(QPoint(-3, hh))
        self.nex_btn.move(QPoint(w - 15, hh))
        self._show_btns()

    def _hum_convert(self, value: int) -> Tuple[float, str]:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return round(value, 2), units[i]
            value = value / size

    def clear_files(self):
        self.clear()
        self._add_upload_state()
        self.file_changed.emit()

    def set_max_file_size(self, size: int) -> None:
        self._max_file_size = size

    def set_max_file_count(self, count: int) -> None:
        self._max_files = count

    def max_file_size(self) -> Tuple[float, str]:
        value, unit = self._hum_convert(self._max_file_size)
        return value, unit

    @property
    def current_file_count(self):
        count = self.count()
        ret = count - 1
        if ret == -1:
            return 0
        return ret

    @property
    def max_file_size_humen(self) -> str:
        value, unit = self.max_file_size()
        return f'{value}{unit}'

    def add_image_file(self, pixmap: QPixmap) -> bool:

        def left_click(this, e):
            this.__class__.mousePressEvent(this, e)
            if e.button() == Qt.LeftButton:
                self.preview_signal.emit(widget.item)

        def remove_file():
            index = item.data(Qt.UserRole)
            take_item = self.takeItem(index)
            self.removeItemWidget(take_item)
            k = -1
            for i in range(self.count()):
                old_item = self.item(i)
                j = old_item.data(Qt.UserRole)
                if j is not None:
                    k += 1
                    old_item.setData(Qt.UserRole, k)

                if j is None:
                    w = self.itemWidget(old_item)
                    if self.count() >= (self._max_files + 1):
                        w.label.setPixmap(
                            QPixmap(self.forbib_img).scaled(25, 25, transformMode=Qt.SmoothTransformation))
                        self.add_widget.text_label.setText('禁止添加')
                        w.setEnabled(False)
                    else:
                        w.label.setPixmap(
                            QPixmap(self.upload_img).scaled(30, 30, transformMode=Qt.SmoothTransformation))
                        self.add_widget.text_label.setText('请上传图片')
                        w.setEnabled(True)
            self.file_changed.emit()

        if self.can_add():
            self._remove_upload_state()
            h = self.widget_size  # 80
            image_index = self.count()
            item = QListWidgetItem()
            item.setData(Qt.UserRole, image_index)
            item.setSizeHint(QSize(h, h))

            widget = QWidget()
            widget.mousePressEvent = MethodType(left_click, widget)
            widget.item = item
            widget.setStyleSheet(
                'QWidget{border:2px dashed lightgray}QWidget:hover{border:2px dashed #426BDD}')
            widget.setFixedSize(QSize(h, h))

            lay = QVBoxLayout(widget)
            lay.setSpacing(0)
            lay.setContentsMargins(2, 2, 2, 2)

            frame = QFrame()
            frame.setStyleSheet('border:none')
            frame.setFrameShape(QFrame.NoFrame)
            frame_lay = QHBoxLayout(frame)
            frame_lay.setSpacing(0)
            frame_lay.setContentsMargins(0, 0, 0, 0)
            frame_lay.addSpacerItem(QSpacerItem(
                20, 20, hPolicy=QSizePolicy.Expanding))

            remove_btn = QPushButton()
            remove_btn.setCursor(Qt.PointingHandCursor)
            remove_btn.setStyleSheet('''
                QPushButton{border:none;background-color: transparent;image: url(:/imgs/移除(1).svg)}
                QPushButton:hover{border:none;image: url(:/imgs/移除.svg)}''')
            remove_btn.setToolTip('移除')
            frame_lay.addWidget(remove_btn, 0)
            remove_btn.clicked.connect(remove_file)

            label = QLabel()
            label.setMaximumWidth(h - 4)
            label.setStyleSheet('border:none')
            label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            label.setAlignment(Qt.AlignCenter)
            label.setScaledContents(True)
            label.setPixmap(pixmap)

            lay.addWidget(frame, 0)
            lay.addWidget(label, 1)

            widget.label = label

            self.addItem(item)
            self.setItemWidget(item, widget)

            self._add_upload_state()
            self.file_changed.emit()
            return True
        return False

    def remove_image_file(self, index: int) -> None:
        item = self.item(index)
        index = item.data(Qt.UserRole)
        if index is not None:
            take_item = self.takeItem(index)
            self.removeItemWidget(take_item)

            k = -1
            for i in range(self.count()):
                old_item = self.item(i)
                j = old_item.data(Qt.UserRole)
                if j is not None:
                    k += 1
                    old_item.setData(Qt.UserRole, k)

                if j is None:
                    w = self.itemWidget(old_item)
                    if self.count() >= (self._max_files + 1):
                        w.label.setPixmap(
                            QPixmap(self.forbib_img).scaled(25, 25, transformMode=Qt.SmoothTransformation))
                        w.text_label.setText('禁止添加')
                        w.setEnabled(False)
                    else:
                        w.label.setPixmap(
                            QPixmap(self.upload_img).scaled(30, 30, transformMode=Qt.SmoothTransformation))
                        self.add_widget.text_label.setText('请上传图片')
                        w.setEnabled(True)
            self.file_changed.emit()

    def get_upload_files(self) -> List[bytes]:
        res = []
        for i in range(self.count()):
            item = self.item(i)
            data = item.data(Qt.UserRole)
            if data is not None:
                w = self.itemWidget(item)
                pixmap = w.label.pixmap()
                data = self._pixmap_to_bytes(pixmap)
                # Path.home().joinpath(f'desktop/__{i}__.png').write_bytes(data)
                res.append(data)
        return res

    def get_upload_pixmaps(self) -> List[QPixmap]:
        res = []
        for i in range(self.count()):
            item = self.item(i)
            data = item.data(Qt.UserRole)
            if data is not None:
                w = self.itemWidget(item)
                pixmap = w.label.pixmap()
                res.append(pixmap)
        return res

    def can_add(self) -> bool:
        return self.count() < (self._max_files + 1)

    def set_max_files(self, value: int) -> None:
        self._max_files = value

    def max_file_count(self) -> int:
        return self._max_files

    def _add_upload_state(self):
        def open_file():
            file, _ = QFileDialog.getOpenFileName(self, '选择上传图片', Path.home().joinpath('desktop').__str__(),
                                                  '*.png;*.jpg;*.jpeg')
            if file:
                size = Path(file).stat().st_size
                if size >= self._max_file_size:
                    self.file_size_max.emit(self.max_file_size_humen)
                else:
                    self.add_image_file(QPixmap(file))

        def click(this, event):
            this.__class__.mousePressEvent(this, event)
            if event.button() == Qt.LeftButton:
                open_file()

        item = QListWidgetItem()
        h = self.widget_size
        item.setSizeHint(QSize(h, h))
        item.setData(Qt.UserRole, None)
        widget = QWidget()
        widget.mousePressEvent = MethodType(click, widget)
        widget.setStyleSheet(
            'QWidget{border:2px dashed lightgray; border-radius:3px}QWidget:hover{border:2px dashed #426BDD}')
        lay = QVBoxLayout(widget)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        widget.setFixedHeight(h)
        widget.setFixedWidth(h)
        widget.setCursor(Qt.PointingHandCursor)

        lay.addSpacerItem(QSpacerItem(20, 20, vPolicy=QSizePolicy.Expanding))
        label = QLabel()
        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        label.setAlignment(Qt.AlignCenter)
        label.setPixmap(QPixmap(self.upload_img).scaled(
            30, 30, transformMode=Qt.SmoothTransformation))
        label.setStyleSheet('border:none;background-color:transparent')
        lay.addWidget(label, 1)
        text_label = QLabel()
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet('font-family:微软雅黑;color: gray;border:none')
        text_label.setText('请上传图片')
        lay.addWidget(text_label, 0)
        lay.addSpacerItem(QSpacerItem(20, 20, vPolicy=QSizePolicy.Expanding))

        widget.label = label
        widget.text_label = text_label

        self.add_widget = widget

        self.addItem(item)
        self.setItemWidget(item, widget)

        if self.count() >= (self._max_files + 1):
            widget.setEnabled(False)
            text_label.setText('禁止添加')
            label.setPixmap(QPixmap(self.forbib_img).scaled(
                25, 25, transformMode=Qt.SmoothTransformation))

    def _remove_upload_state(self):
        for i in range(self.count()):
            item = self.item(i)
            data = item.data(Qt.UserRole)
            if data is None:
                self.takeItem(i)
                self.removeItemWidget(item)
                self.add_widget = None
                break

    def _pixmap_to_bytes(self, pixmap: QPixmap, format: str = 'JPG') -> Optional[bytes]:
        bytes_data = QByteArray()
        buf = QBuffer(bytes_data)
        pixmap.save(buf, 'PNG')
        data = bytes(bytes_data)
        if len(data) <= self._max_file_size:
            return data

        else:
            bytes_data = QByteArray()
            buf = QBuffer(bytes_data)
            pixmap.save(buf, format)
            data = bytes(bytes_data)

            if len(data) <= self._max_file_size:
                return data

            qua = 50

            while True:
                bytes_data = QByteArray()
                buf = QBuffer(bytes_data)
                pixmap.save(buf, format, qua)
                data = bytes(bytes_data)
                if len(data) >= self._max_file_size:
                    if qua <= 0:
                        return
                    qua -= 5
                else:
                    return data


class TableWidget(QTableWidget):

    def set_headers(self, texts: List[str]):
        for index, txt in enumerate(texts):
            item = self.horizontalHeaderItem(index)
            if item is not None:
                item.setText(txt)

    def __init__(self, *a, **kw):
        super(TableWidget, self).__init__(*a, **kw)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        horizon = self.horizontalHeader()
        horizon.setSectionResizeMode(QHeaderView.Stretch)
        horizon.setSectionResizeMode(0, QHeaderView.Fixed)
        horizon.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        horizon.setSectionResizeMode(6, QHeaderView.Fixed)

        horizon.setStyleSheet(Sh.header_view_style3)  # 表格样式设计
        self.verticalScrollBar().setStyleSheet(Sh.history_v_scroll_style)

        self.setColumnWidth(0, 25)
        self.setColumnWidth(6, 35)
        self.setSelectionMode(QTableWidget.NoSelection)

        # 去除选中虚线框和背景
        self.setFocusPolicy(Qt.NoFocus)
        self.verticalHeader().hide()
        self.setMouseTracking(True)
        self.setStyleSheet('border: none; background: white')
        self.setShowGrid(False)
        # self.cellEntered.connect(row_style)
        # self.cellClicked.connect(click_cell)


class InfoLabel(QLabel):

    def _wrap(self, string, max_width=25) -> str:
        result1 = [string[i:i + max_width]
                   for i in range(0, len(string), max_width)]
        result = '\n'.join(result1)
        return result

    def __init__(self, *a, **kw):
        super(InfoLabel, self).__init__(*a, **kw)
        self._text = ''

    @property
    def raw_text(self):
        return self._text

    def setText(self, a0: str, tool_tip=True, width=40) -> None:
        super().setText(a0)
        self._text = a0
        self.setToolTip(a0, width)

    def clear(self) -> None:
        super(InfoLabel, self).clear()
        self._text = ''

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        if self._text:
            fm = self.fontMetrics()
            text = fm.elidedText(self._text, Qt.ElideRight, self.width())
            super().setText(text)

    def setToolTip(self, a0: str, width=25) -> None:
        if width is not None:
            text = self._wrap(a0, width)
        else:
            text = a0
        super().setToolTip(text)

    def enterEvent(self, a0) -> None:
        super(InfoLabel, self).enterEvent(a0)


class ThumLabel(QLabel):
    show_sig = pyqtSignal(QPixmap, dict)
    select_sig = pyqtSignal()
    history_sig = pyqtSignal(object)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.histort_widget = None
        self.data = None

        button = QPushButton(self)
        button.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        button.setIcon(QIcon(":/imgs/放大镜.svg"))
        button.setStyleSheet("border:none")
        self.button = button
        self.setCursor(QCursor(Qt.PointingHandCursor))
        # self.button.clicked.connect(
        #     lambda: self.show_sig.emit(self.pixmap(), self.histort_widget.get_data())
        # )
        self.setStyleSheet('border:1px solid lightgray')

    def set_history(self, h):
        self.histort_widget = h

    def adjust_btn(self):
        x = self.width() - self.button.width()
        y = self.height() - self.button.height()
        self.button.move(x, y)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            pixmap = self.pixmap()
            if pixmap:
                if not pixmap.isNull():
                    self.show_sig.emit(
                        self.pixmap(), self.histort_widget.get_data())
                    self.history_sig.emit(self.data)

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        self.adjust_btn()


class GrabLabel(QLabel):
    show_sig = pyqtSignal(QPixmap)
    select_sig = pyqtSignal()

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

        button = QPushButton(self)
        button.setIcon(QIcon(":/imgs/fangdajing.svg"))
        button.setStyleSheet("border:none")
        self.button = button
        self.button.clicked.connect(lambda: self.show_sig.emit(self.pixmap()))
        self.button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        select_button = QPushButton(self)
        select_button.setIcon(QIcon(":/imgs/图片红色.svg"))
        select_button.setStyleSheet("border:none")
        self.select_button = select_button
        self.select_button.clicked.connect(lambda: self.select_sig.emit())
        self.button.hide()
        self.select_button.setCursor(
            QCursor(Qt.CursorShape.PointingHandCursor))
        self.select_button.hide()

    def enterEvent(self, a0) -> None:
        super().enterEvent(a0)
        self.button.show()
        x, y = self.button.width(), self.button.height()
        self.select_button.move(x + 5, 0)
        self.select_button.show()

    def leaveEvent(self, a0) -> None:
        super().leaveEvent(a0)
        self.button.hide()
        self.select_button.hide()


class CapkeysLineEdit(QLineEdit):
    keys_signal = pyqtSignal(list)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._current_short = []

    def keyPressEvent(self, a0: QKeyEvent):
        modfiers = set()
        keys = set()
        true_m = None
        true_key = None
        ks = "abcdefghijklmnopqrstuvwxyz"
        for k in ks:
            if a0.key() == getattr(Qt.Key, "Key_%s" % k.upper()):
                keys.add(k.upper())
                true_key = a0.key()
        if a0.modifiers() == Qt.KeyboardModifier.ControlModifier:
            modfiers.add("CTRL")
            true_m = a0.modifiers()
        elif a0.modifiers() == Qt.KeyboardModifier.AltModifier:
            modfiers.add("ALT")
            true_m = a0.modifiers()
        try:
            m = modfiers.pop()
        except:
            m = ""
        try:
            k = keys.pop()
        except:
            k = ""
        if m:
            super().keyPressEvent(a0)
            self.setText(f"{m}+{k}")
            self._current_short.append(true_key)
            self._current_short.append(true_m)


Size = Tuple[int, int]
Zoom = Tuple[float, float]
RectCoord = List[int]  # [x1,y1,x2,y2]
RectCoords = List[RectCoord]  # [[x1,y1,x2,y2], [x2,y3,x4,y4], ...]
Region = 'x1,y1,x2,y2;...'


class Actions(Enum):
    MOVE_RECT = 0
    DRAW_RECT = 1
    NONE = 2
    ERASE = 3  # 图像编辑擦除
    NORMAL = 4  # 正常模式
    ZOOM = 5  # 缩放模式
    MOVE = 6  # 移动模式


class Validpoints(QObject):  # [[x1,y1, x2, y2], ...]

    points_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.__data = []

    @classmethod
    def fromList(points: RectCoords):
        point = Validpoints()
        point.appends(points)
        return point

    @classmethod
    def adjustCoords(cls, points: RectCoords) -> RectCoords:
        xycoords = []
        for coord in points:
            x1, y1, x2, y2 = coord
            w, h = abs(x2 - x1), abs(y2 - y1)
            if (x2 - x1) > 0 and (y2 - y1) > 0:
                xycoords.append([x1, y1, x2, y2])  # 右下方滑动
            elif (x2 - x1) > 0 and (y2 - y1) < 0:
                xycoords.append([x1, y1 - h, x2, y2 + h])  # 右上方滑动
            elif (x2 - x1) < 0 and (y2 - y1) > 0:
                xycoords.append([x2, y2 - h, x1, y1 + h])  # 左下方滑动
            else:
                xycoords.append([x2, y2, x1, y1])  # 左上方滑动
        return xycoords

    @property
    def data(self) -> RectCoords:
        res = []
        for v in self.__data:
            if (v[:2] != v[2:]) and (0 not in v[-2:]):
                res.append(v)
        return res

    def append(self, v: RectCoord) -> bool:
        if v[:2] != v[2:]:
            self.__data.append(v)
            return True
        return False

    def appends(self, points: RectCoords) -> None:
        for point in points:
            self.append(point)

    def appendRect(self, qrect: QRect) -> bool:
        rects = list(qrect.getCoords())
        return self.append(rects)

    def appendRects(self, qrects: List[QRect]) -> None:
        for rect in qrects:
            self.appendRect(rect)

    def appendRectslike(self, qrects_like: List[tuple]) -> None:
        for rect in qrects_like:
            self.appendRect(QRect(*rect))

    def clear(self):
        self.__data.clear()

    def __iter__(self):
        for v in self.data:
            yield v

    def __getitem__(self, item) -> RectCoord:
        return self.__data[item]

    def __repr__(self):
        return f'Validpoints<{self.data}>'


class ImgLabel(QLabel):
    start_point: QPoint = None
    PEN = QPen(Qt.darkYellow, 2, Qt.DashLine)
    FILL_COLOR = QColor(50, 50, 50, 30)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.edited = True
        self.points = Validpoints()  # 矩形区域
        self.menu = QMenu(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setAlignment(Qt.AlignCenter)
        # self.customContextMenuRequested.connect(self.contextMenu)

    def setEdit(self, flag: bool):
        self.edited = flag
        self._width = self.pixmap().width()
        self._heigth = self.pixmap().height()

    def contextMenu(self, pos):
        menu = QMenu(self)
        a1 = menu.addAction('清除')
        a2 = menu.addAction('确认')
        action = menu.exec_(QCursor.pos())
        if action == a1:
            self.points.clear()
            self.points.points_signal.emit([])
            self.update()
        elif action == a2:
            points = []
            for xycoords in self.points.data:
                x1, y1, x2, y2 = xycoords
                w, h = abs(x2 - x1), abs(y2 - y1)
                if (x2 - x1) > 0 and (y2 - y1) > 0:
                    points.append([x1, y1, x2, y2])  # 右下方滑动
                elif (x2 - x1) > 0 and (y2 - y1) < 0:
                    points.append([x1, y1 - h, x2, y2 + h])  # 右上方滑动
                elif (x2 - x1) < 0 and (y2 - y1) > 0:
                    points.append([x2, y2 - h, x1, y1 + h])  # 左下方滑动
                else:
                    points.append([x2, y2, x1, y1])  # 左上方滑动
            self.points.clear()
            self.points.appends(points)
            self.points.points_signal.emit(points)

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.start_point = QMouseEvent.pos()

        if self.edited:
            if QMouseEvent.button() == Qt.LeftButton:
                self.points.append([QMouseEvent.x(), QMouseEvent.y(), 0, 0])
        else:
            super().mousePressEvent(QMouseEvent)

    def mouseMoveEvent(self, QMouseEvent):
        if self.edited:
            if (QMouseEvent.buttons()
                & Qt.LeftButton) and self.rect().contains(
                QMouseEvent.pos()):
                self.points[-1][-2:] = [QMouseEvent.x(), QMouseEvent.y()]
                self.update()
        else:
            super().mouseMoveEvent(QMouseEvent)

    def paintEvent(self, QPaintEvent):
        if self.edited:
            self.setCursor(Qt.CrossCursor)
            font = self.font()
            font.setPointSize(15)
            painter = QPainter()
            painter.begin(self)
            painter.setFont(font)
            self.drawPolicy(painter)
            painter.end()
        else:
            self.setCursor(Qt.ArrowCursor)
            super().paintEvent(QPaintEvent)

    def drawPolicy(self, painter):
        painter.drawPixmap(0, 0, self.pixmap())
        if self.points.data:
            painter.setPen(self.PEN)
            for index, point in enumerate(self.points.data, 1):
                x1, y1, x2, y2 = point
                msg = str(index)
                w, h = abs(x2 - x1), abs(y2 - y1)
                if (x2 - x1) > 0 and (y2 - y1) > 0:
                    painter.drawRect(x1, y1, w, h)  # 右下方滑动
                    painter.drawText(x1, y1 - 4, msg)
                    painter.fillRect(x1, y1, w, h, self.FILL_COLOR)
                elif (x2 - x1) > 0 and (y2 - y1) < 0:
                    painter.drawRect(x1, y1 - h, w, h)  # 右上方滑动
                    painter.drawText(x1, y2 - 4, msg)
                    painter.fillRect(x1, y1 - h, w, h, self.FILL_COLOR)

                elif (x2 - x1) < 0 and (y2 - y1) > 0:
                    painter.drawRect(x1 - w, y1, w, h)  # 左下方滑动
                    painter.drawText(x2, y1 - 4, msg)
                    painter.fillRect(x1 - w, y1, w, h, self.FILL_COLOR)

                else:
                    painter.drawRect(x2, y1 - h, w, h)  # 左上方滑动
                    painter.drawText(x2, y2 - 4, msg)
                    painter.fillRect(x2, y1 - h, w, h, self.FILL_COLOR)


class ZoomLabel(ImgLabel):
    drag_enable = True  # 是否拖拽
    viewpoint_zoom = True  # 缩放类型: 视点缩放, 普通缩放
    resize_auto_scaled = False  # 自身尺寸变化
    action = Actions.NONE

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFocusPolicy(Qt.NoFocus)
        self.zoomAndMoveInit()  # 缩放,移动初始化
        # self.erase_cursor = QCursor(QPixmap('./sources/eraser_mouse.png').scaled(32, 32, transformMode=Qt.SmoothTransformation), 2, 18)

    def zoomAndMoveInit(self):
        self.setMouseTracking(True)  # 设置光标追踪
        self.move_intention = False  # 控制拖拽移动相关的标志位
        self.zoom_intention = False  # 控制缩放相关的标志位
        self.pixmap_draw = None  # 需要绘制的图片资源
        self.pixmap_draw_rect = None  # 绘图区域,pixmap绘制在qrect中,控制qrect即可控制pixmap的拖拽,缩放等行为
        self.pixmap_raw = None
        self.pixmap_point = None
        self.pixmap_is_max = False
        self.wheel_logs = deque(maxlen=2)

    def activeAction(self):
        return self.action

    def setAction(self, action: Actions):
        self.action = action

    def isInPixmap(self, point: QPoint):
        return self.pixmap_draw_rect.contains(point)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Control:  # 按下ctrl 进入缩放模式
            self.zoom_intention = True
            self.setCursor(Qt.PointingHandCursor)
            self.setAction(Actions.ZOOM)

    def keyReleaseEvent(self, event):
        super().keyReleaseEvent(event)  # 取消ctrl 取消缩放模式
        if event.key() == Qt.Key_Control:
            self.zoom_intention = False
            self.setCursor(Qt.ClosedHandCursor)
            self.action = Actions.NORMAL

    def mousePressEvent(self, QMouseEvent: QMouseEvent):
        super().mousePressEvent(QMouseEvent)
        if self.pixmap_draw:
            if QMouseEvent.button() == Qt.LeftButton:
                if self.action == Actions.DRAW_RECT:
                    self.points.append(
                        [QMouseEvent.x(), QMouseEvent.y(), 0, 0])
                elif self.action == Actions.ERASE:
                    self.erase_points.append(
                        [QMouseEvent.x(), QMouseEvent.y(), 0, 0])
                if self.isInPixmap(QMouseEvent.pos()):  # 初始化
                    self.move_intention = True
                    self.start_pos = QMouseEvent.pos()
                    self.pixmap_left_before = self.pixmap_draw_rect.topLeft()

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.move_intention = False

    def mouseMoveEvent(self, QMouseEvent):
        super().mouseMoveEvent(QMouseEvent)
        # self.setFocus() # 获取焦点
        if self.pixmap_draw:  # 画图标志位置
            if self.drag_enable:  # 是否拖拽
                if self.isInPixmap(QMouseEvent.pos()):  # 设置移动光标样式,拖拽设置
                    if self.move_intention:
                        self.setCursor(Qt.ClosedHandCursor)
                if self.move_intention and not self.zoom_intention:  # 拖拽图片
                    self.setAction(Actions.MOVE)
                    self.current_pos = QMouseEvent.pos()
                    distance = self.current_pos - self.start_pos
                    self.pixmap_draw_rect.moveTo(
                        self.pixmap_left_before + distance)
                    self._moveAfterUpdateZoomParamters()
                    self.update()

    def wheelEvent(self, QWheelEvent: QWheelEvent):
        super().wheelEvent(QWheelEvent)
        # if self.pixmap_draw_rect.contains(QWheelEvent.pos()) and self.zoom_intention:
        if self.pixmap_draw_rect.contains(QWheelEvent.pos()):
            self.action = Actions.ZOOM
            self._zoomBeforeParametersCalculate(QWheelEvent)
            self._zoomCalculate(QWheelEvent)
            self._zoomAfterupdateParameters(QRect(self.pixmap_draw_rect))
            self.update()

    def setPixmap(self, pixmap):
        raise RuntimeError('use addPixmap, not setPixmap')

    # 添加显示的图片, 默认全部显示范围
    def addPixmap(self, source: str = None, point: QPoint = None, *, fixed=True,
                  margins: QMargins = QMargins(0, 0, 0, 0), action: Actions = Actions.NORMAL):
        self.drag_enable = fixed
        self.pixmap_draw = QPixmap(source)  # 图片
        self.pixmap_raw = source  # 原始图片
        super().setPixmap(self.pixmap_draw)  # 添加pixmap
        self.setAction(action)  # 设置标志位
        pixmap_rect = self.pixmap_draw.size()
        rect = self.size()
        flag = pixmap_rect - rect
        if flag.width() > 0 or flag.height() > 0:
            scaled = rect.width() / pixmap_rect.width()
            scaled_h = rect.height() / pixmap_rect.height()
            scaled = min(scaled, scaled_h)

            height = int(scaled * pixmap_rect.height())
            width = int(rect.width() * scaled)
            x = (rect.width() - width) / 2
            y = (rect.height() - height) / 2
            rect = QRect(x, y, width, height)
            if point is not None:
                rect = QRect(point, rect.size())
        else:
            rect = self.pixmap_draw.rect()
            s = self.size() - self.pixmap_draw.size()
            rect = QRect(s.width() / 2, s.height() / 2,
                         rect.width(), rect.height())
            if point is not None:
                rect = QRect(point, self.pixmap_draw.size())

        if margins.isNull():
            self.pixmap_draw_rect = QRect(rect)  # 初始绘图区域
            self.pixmap_left_before = QRect(
                rect).topLeft()  # 初始绘画区域左上角, 控制拖拽移动的相关参数
            self.zoom_default_rect = QRect(rect)  # 光标缩放参数初始化
            self.default_rect = QRect(rect)  # 备份初始绘画区域
        else:
            self.pixmap_draw_rect = QRect(rect).marginsAdded(margins)  # 初始绘图区域
            self.pixmap_left_before = QRect(rect).marginsAdded(
                margins).topLeft()  # 初始绘画区域左上角, 控制拖拽移动的相关参数
            self.zoom_default_rect = QRect(
                rect).marginsAdded(margins)  # 光标缩放参数初始化
        self._restore = False
        self.update()

    def setPixmapVHCenter(self):
        self.pixmap_draw_rect.moveCenter(self.rect().center())
        self._moveAfterUpdateZoomParamters()

    # 计算视点缩放的相关参数(计算当前坐标和zoom_default_rect 左上角坐标的斜率与长度)
    def _calcAnglelength(self, left_top: QPoint, second: QPoint):  # 返回弧度, 长度
        pa_x = left_top.x()
        pa_y = left_top.y()
        pb_x = second.x()
        pb_y = second.y()
        x = pb_x - pa_x
        c = math.sqrt(math.pow(pb_y - pa_y, 2) + math.pow(pb_x - pa_x, 2))
        cosAgl = x / c
        angle = math.acos(cosAgl)
        return angle, c

    # 缩放后更新视点缩放相关参数
    def _zoomAfterupdateParameters(self, rect: QRect, current_point: QPoint = None):
        self.zoom_default_rect = QRect(rect)

    # 缩放前视点相关参数的计算
    def _zoomBeforeParametersCalculate(self, wheelEvent: QWheelEvent):
        left_top = self.zoom_default_rect.topLeft()
        current = wheelEvent.pos()
        self.topleft_angle, self.topleft_distance = self._calcAnglelength(
            left_top, current)

    # 图片拖拽后需更新视点缩放相关参数
    def _moveAfterUpdateZoomParamters(self):
        if self.viewpoint_zoom:
            self.zoom_default_rect = QRect(self.pixmap_draw_rect)

    # 图片缩放计算
    def _zoomCalculate(self, wheelEvent: QWheelEvent):
        # self.__pdfwidget.zoom_flag = -1  # 其他
        angle = wheelEvent.angleDelta() / 8
        if angle.y() < 0:  # 图像减小
            w, h = self.pixmap_draw_rect.width() * .95, self.pixmap_draw_rect.height() * .95
            self.pixmap_draw_rect.setSize(QSize(w, h))
            self._restore = False
            self.wheel_logs.append(False)
        else:  # 图像放大
            w, h = self.pixmap_draw_rect.width() * 1.05, self.pixmap_draw_rect.height() * 1.05
            flag_size = QSize(w, h) - self.pixmap_raw.size()
            if flag_size.width() >= 0 or flag_size.height() >= 0:
                self._restore = True
                self.wheel_logs.append(True)
            else:
                self.pixmap_draw_rect.setSize(QSize(w, h))

        zoom = self.pixmap_draw_rect.width() / self.zoom_default_rect.width()  # 缩放倍数
        if zoom >= 1:
            # self.pixmap_draw = self.pixmap_draw.scaled(w, h, transformMode=Qt.SmoothTransformation) # 更新图片
            pass
        if self.resize_auto_scaled:
            self.setFixedSize(QSize(w, h))
        if self.viewpoint_zoom:
            # 更新位置,保持视点不变
            new_left_x = self.zoom_default_rect.x() - self.topleft_distance * \
                         (zoom - 1) * math.cos(self.topleft_angle)
            new_left_y = self.zoom_default_rect.y() - self.topleft_distance * \
                         (zoom - 1) * math.sin(self.topleft_angle)
            self.pixmap_draw_rect.moveTo(QPoint(new_left_x, new_left_y))

    def enterEvent(self, event):
        self.grabKeyboard()
        return super().enterEvent(event)

    def leaveEvent(self, event):
        self.releaseKeyboard()
        return super().leaveEvent(event)

    # override
    def drawPolicy(self, painter):
        painter.setPen(self.PEN)
        if self.action == Actions.ZOOM or self.action == Actions.MOVE or self.action == Actions.NORMAL:
            painter.save()
            painter.setPen(QPen(QColor('#B7B7B7'), 2))  # 设置边框颜色
            painter.setRenderHint(QPainter.Antialiasing)
            if self._restore:
                logs: deque = self.wheel_logs
                if len(logs) <= 1:
                    self.addPixmap(self.pixmap_raw,
                                   self.pixmap_draw_rect.topLeft())
                else:
                    if all(logs):
                        pixmap = self.pixmap_draw
                        painter.drawPixmap(
                            self.pixmap_draw_rect, pixmap)  # 限制在rect
                        painter.drawRect(self.pixmap_draw_rect)
                    else:
                        self.addPixmap(self.pixmap_raw,
                                       self.pixmap_draw_rect.topLeft())
            else:
                pixmap = self.pixmap_draw.scaled(self.pixmap_draw_rect.size(), aspectRatioMode=Qt.KeepAspectRatio,
                                                 transformMode=Qt.SmoothTransformation)
                painter.drawPixmap(self.pixmap_draw_rect, pixmap)  # 限制在rect
                painter.drawRect(self.pixmap_draw_rect)
            painter.restore()

    # override
    def paintEvent(self, QPaintEvent):
        if self.edited:
            font = self.font()
            font.setPointSize(15)
            painter = QPainter()
            painter.begin(self)
            painter.setFont(font)
            self.drawPolicy(painter)
            painter.end()
        else:
            super().paintEvent(QPaintEvent)


class ImagesListLabel(QWidget):
    class LoadState(IntEnum):
        not_set = -1  # 初始状态
        fail = 0  # 请求失败
        success = 1  # 图片加载成功
        broken = 2  # 请求成功, 但返回无效图片

    class RoundList(object):

        def __init__(self, data: Union[List[str], List[bytes]] = None) -> None:
            if data:
                self._data = [(url, ImagesListLabel.LoadState.not_set)
                              for url in list(data)]
            else:
                self._data = []

            self._len = len(self._data)
            self._index = -1

        @property
        def current(self):
            return self._index

        def set_data(self, data: Union[List[str], List[bytes]]):
            self._data = [(url, ImagesListLabel.LoadState.not_set)
                          for url in list(data)]
            self._len = len(self._data)

        def length(self):
            return self._len

        def update(self, index, value):
            self._data[index] = value

        def next(self, index: int = None):
            if self._len:

                if index is not None:
                    self._index = index

                i = self._index + 1
                if i == self._len:
                    self._index = 0
                else:
                    self._index = i
                return self._data[self._index]

        def previous(self, index: int = None):
            if self._len:

                if index is not None:
                    self._index = index

                if self._index == -1 or self._index == 0:
                    self._index = self._len - 1
                else:
                    self._index -= 1
                return self._data[self._index]

        def reset(self):
            self._index = -1

    def save(self):
        self._keep = True
        if not self.pixmap().isNull():
            fmt = datetime.now().strftime('%Y%m%d%H%M%S')
            file, _ = QFileDialog.getSaveFileName(
                self, '保存图片', Path.cwd().joinpath(f'百舟打款助手_{fmt}.png').__str__(), '*.png;')
            if file:
                self.pixmap().save(file)
                Message.info(f'图片已保存: {file}', self)
        del self._keep

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        # self.setAlignment(Qt.AlignCenter)
        self._window_size = QApplication.desktop().size()
        self._worker = kwargs.pop('worker', None)
        self._image_urls = self.RoundList()
        self._image_title = None
        self._max_show_size: QSize = QApplication.desktop().size() * 2 / 3
        self.mPos: QPoint = None

        self.setFixedSize(self._max_show_size)

        btn_style = '''
            QPushButton{border:none;background-color:transparent;color:white}
        '''

        btn_f = self.fontMetrics().width('abc') * 2
        self._next_btn = QPushButton(self)
        self._next_btn.setIcon(QIcon(':/imgs/前进面性(1).svg'))
        self._next_btn.setToolTip('下一张')
        self._next_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._next_btn.setShortcut(QKeySequence(Qt.Key_Right))

        self._previous_btn = QPushButton(self)
        self._previous_btn.setIcon(QIcon(':/imgs/后退面性(1).svg'))
        self._previous_btn.setToolTip('上一张')
        self._previous_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._previous_btn.setShortcut(QKeySequence(Qt.Key_Left))

        self._next_btn.setStyleSheet(btn_style)
        self._previous_btn.setStyleSheet(btn_style)

        self._loading_label = GifLabel(self)
        self._loading_label.setStyleSheet(
            'border:none;background-color: transparent')
        self._loading_label.setFixedWidth(btn_f * 2)

        self._text_label = QLabel(self)
        self._text_label.setStyleSheet(
            'border:none;font-family:微软雅黑;color:white')
        self._text_label.setAlignment(Qt.AlignCenter)

        self._title_label = QLabel(self)
        self._title_label.setStyleSheet(
            'border:none;font-family:微软雅黑;color:white')
        self._title_label.setAlignment(Qt.AlignLeft)
        self._title_label.setIndent(30)

        self._close_btn = QPushButton(self)
        self._close_btn.setIcon(QIcon(':/imgs/关闭.svg'))
        self._close_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._close_btn.setStyleSheet(btn_style)
        self._close_btn.setToolTip('退出')
        self._close_btn.setShortcut('Esc')

        self._down_load = QPushButton(self)
        self._down_load.setIcon(QIcon(':/imgs/排序.svg'))
        self._down_load.setCursor(QCursor(Qt.PointingHandCursor))
        self._down_load.setStyleSheet(btn_style)
        self._down_load.setToolTip('保存图片')
        self._down_load.clicked.connect(self.save)

        self._next_btn.setFixedWidth(btn_f)
        self._previous_btn.setFixedWidth(btn_f)
        self._close_btn.setFixedWidth(btn_f)

        self._next_btn.show()
        self._previous_btn.show()

        self._next_btn.clicked.connect(lambda: self.next_image())
        self._previous_btn.clicked.connect(lambda: self.previous_image())
        self._close_btn.clicked.connect(self.close)

        self.setStyleSheet('border:none;background-color: rgb(50,50,50)')

        self._zoom_label = ZoomLabel(self)
        self._zoom_label.setFixedSize(self.width() - 80, self.height() - 30)
        self._zoom_label.move(40, 30)

        self.installEventFilter(self)

    def set_worker(self, worker: 'BackgroundWorker'):
        self._worker = worker

    def set_image_contents(self, imgs: Union[List[str], List[bytes]]):
        # print('set contents', len(imgs))
        res = []
        j = -1
        for v in imgs:
            j += 1
            if not isinstance(v, (tuple, list)):
                res.append((v, j))
            else:
                res.append(v)
        self._image_urls = self.RoundList(res)

    def _reset(self):
        self._image_urls.reset()

    # ??
    def _get_image(self, url, index) -> None:

        async def _fetch_image(url, index):
            """
            异步加载图片
            """
            await asyncio.sleep(2)
            return url, index

        def call_back(ret):
            url, index = ret
            pixmap = QPixmap(url)
            self._image_urls.update(index, (pixmap, self.LoadState.success))
            print(index, url)

        def err_back(error):
            pass

        self._worker.add_coro(_fetch_image(url, index), call_back=call_back)

    def set_images_title(self, title: str):
        self._title_label.setText(title)

    def next_image(self, index: int = None):
        pic = self._image_urls.next(index)
        text_msg = f'{self._image_urls.current + 1}/{self._image_urls.length()}'
        if pic:
            data, state = pic
            if data[0]:
                if isinstance(data[0], str):
                    pixmap = QPixmap(data[0])
                    self._zoom_label.addPixmap(pixmap)
                    # try:
                    #     flag = pixmap.size() - self._max_show_size
                    #     if flag.width() > 0 or flag.height() > 0:
                    #         pixmap = pixmap.scaled(self._max_show_size, aspectRatioMode=Qt.KeepAspectRatio,
                    #                                transformMode=Qt.SmoothTransformation)
                    # except:
                    #     pass
                    # self.setPixmap(pixmap)
                    self._text_label.setText(text_msg)
                elif isinstance(data[0], bytes):
                    pixmap = QPixmap()
                    flag = pixmap.loadFromData(data[0])
                    if flag:
                        # print('next -iamge ', pixmap)
                        self._zoom_label.addPixmap(pixmap)
                        # try:
                        #     pixmap_flag = pixmap.size() - self._max_show_size
                        #     if pixmap_flag.width() > 0 or pixmap_flag.height() > 0:
                        #         pixmap = pixmap.scaled(self._max_show_size, aspectRatioMode=Qt.KeepAspectRatio,
                        #                                transformMode=Qt.SmoothTransformation)
                        # except:
                        #     pass
                        # self.setPixmap(pixmap)
                    else:
                        self.fail_fetch()
                    self._text_label.setText(text_msg)

                elif isinstance(data[0], QPixmap):
                    try:
                        pixmap = QPixmap(data[0])
                        self._zoom_label.addPixmap(pixmap)
                        # pixmap_flag = pixmap.size() - self._max_show_size
                        # if pixmap_flag.width() > 0 or pixmap_flag.height() > 0:
                        #     pixmap = pixmap.scaled(self._max_show_size, aspectRatioMode=Qt.KeepAspectRatio,
                        #                            transformMode=Qt.SmoothTransformation)
                        # self.setPixmap(pixmap)
                        self._text_label.setText(text_msg)
                    except Exception as e:
                        print(e)
            else:
                self.fail_fetch()

    def previous_image(self, index: int = None):
        pic = self._image_urls.previous(index)
        text_msg = f'{self._image_urls.current + 1}/{self._image_urls.length()}'
        if pic:
            data, state = pic
            if data[0]:
                if isinstance(data[0], str):
                    pixmap = QPixmap(data[0])
                    self._zoom_label.addPixmap(pixmap)

                    # flag = pixmap.size() - self._max_show_size
                    # try:
                    #     if flag.width() > 0 or flag.height() > 0:
                    #         pixmap = pixmap.scaled(self._max_show_size, aspectRatioMode=Qt.KeepAspectRatio,
                    #                                transformMode=Qt.SmoothTransformation)
                    # except:
                    #     pass
                    # self.setPixmap(pixmap)
                    self._text_label.setText(text_msg)
                elif isinstance(data[0], bytes):
                    pixmap = QPixmap()
                    flag = pixmap.loadFromData(data[0])
                    if flag:
                        self._zoom_label.addPixmap(pixmap)
                        # try:
                        #     pixmap_flag = pixmap.size() - self._max_show_size
                        #     if pixmap_flag.width() > 0 or pixmap_flag.height() > 0:
                        #         pixmap = pixmap.scaled(self._max_show_size, aspectRatioMode=Qt.KeepAspectRatio,
                        #                                transformMode=Qt.SmoothTransformation)
                        # except:
                        #     pass
                        # self.setPixmap(pixmap)
                    else:
                        self.fail_fetch()
                    self._text_label.setText(text_msg)
                elif isinstance(data[0], QPixmap):
                    pixmap = QPixmap(data[0])
                    self._zoom_label.addPixmap(pixmap)
                    # pixmap_flag = pixmap.size() - self._max_show_size
                    # if pixmap_flag.width() > 0 or pixmap_flag.height() > 0:
                    #     pixmap = pixmap.scaled(self._max_show_size, aspectRatioMode=Qt.KeepAspectRatio,
                    #                            transformMode=Qt.SmoothTransformation)
                    # self.setPixmap(pixmap)
                    self._text_label.setText(text_msg)
            else:
                self.fail_fetch()

    def current_image(self):
        return self.pixmap()

    def pixmap(self) -> QPixmap:
        if isinstance(self._zoom_label.pixmap_raw, QPixmap):
            return self._zoom_label.pixmap_raw
        if self._zoom_label.pixmap_raw is not None:
            return QPixmap(self._zoom_label.pixmap_raw)
        return QPixmap()

    def fail_fetch(self):
        self._zoom_label.addPixmap(QPixmap(':/imgs/损坏(1).svg'), fixed=True)

    def show_label_list(self, index=None, size_scaled=2 / 3):
        self._reset()
        if index is not None:
            f = index - 1
        else:
            f = None
        self.next_image(f)
        size = self._window_size * size_scaled
        self.setFixedSize(size)
        self.show()

    def resizeEvent(self, a0) -> None:
        w, h = self.width(), self.height()
        bw = self._previous_btn.width()
        self._previous_btn.move(10, int(h / 2))

        self._next_btn.move(w - bw - 10, int(h / 2))
        self._next_btn.show()

        self._previous_btn.show()

        hc = w - bw - 10
        self._close_btn.move(hc, 5)
        self._close_btn.show()

        self._down_load.move(hc - 20, 5)
        self._down_load.show()

        hh = int(w - bw) / 2
        self._text_label.move(hh, 5)
        self._text_label.show()

        self._title_label.show()

        self._max_show_size = QSize(
            w - 24, h - self._text_label.fontMetrics().height() - 4)

        # 设置固定尺寸
        self._zoom_label.setFixedSize(w - 80, h - 30)
        self._zoom_label.move(40, 30)
        self._zoom_label.raise_()

        super().resizeEvent(a0)

    def mouseMoveEvent(self, ev: 'QMouseEvent') -> None:
        super().mousePressEvent(ev)
        if ev.buttons() == Qt.LeftButton and self.mPos:
            if self.mPos.y() <= 30:
                self.move(self.mapToGlobal(ev.pos() - self.mPos))

    def mousePressEvent(self, ev) -> None:
        super().mousePressEvent(ev)
        if ev.button() == Qt.LeftButton:
            self.mPos = ev.pos()
            if ev.pos().x() <= self.width() / 2:
                if ev.pos().y() > 30:
                    self._previous_btn.click()
            else:
                if ev.pos().y() > 30:
                    self._next_btn.click()

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a1.type() == QEvent.WindowDeactivate:
            if getattr(self, '_keep', None) is None:
                self.close()
        return QWidget.eventFilter(self, a0, a1)


class Images(ImagesListLabel):

    @classmethod
    def display(cls, pixmaps: Union[List[bytes], List[str]], title: str, target: QWidget = None, index=None):
        self = cls()
        self.set_images_title(title)
        self.set_image_contents(pixmaps)
        self.show_label_list(index)


class GifLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setGif(self, file_name: str) -> None:
        self._movie = QMovie(file_name)
        self._movie.setSpeed(100)
        self.setMovie(self._movie)
        self.movie().start()

    def removeGif(self, text):
        self.setText(text)


class GifButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movie = None
        self._is_loading = False
        self._text: str = ''
        self._start_time = -1
        self._loading_flag = '.'
        self._dynamic = False

    def removeGif(self, icon: str = None, text: str = None):
        self.setEnabled(True)
        _icon = QIcon(icon) if icon is not None else QIcon()
        self.setIcon(_icon)
        if text is not None:
            self.setText(text)

    def setMessage(self, msg: str, icon: str = None):
        self.setText(msg)
        if icon is not None:
            self.setIcon(QIcon(icon))

    def setGif(self, file_name: str, text: str = None, dynamic=False) -> None:
        self.setEnabled(False)
        if text:
            self._text = text
            self.setText(text)
        self._dynamic = dynamic
        self.movie = QMovie(file_name)
        self.movie.setSpeed(100)
        # self.movie.setCacheMode() # 设置帧缓存模式
        self.movie.frameChanged.connect(self._update)
        self.movie.start()
        self._start_time = time.time()

    def setIcon(self, icon: QIcon) -> None:
        if self.movie:
            self.movie.stop()
        super().setIcon(icon)

    def stopGif(self) -> None:
        if self.movie:
            self.movie.stop()

    def reStartGif(self) -> None:
        if self.movie:
            self.movie.start()

    def _update(self, index: int) -> None:
        pixmap = self.movie.currentPixmap()
        super().setIcon(QIcon(pixmap))
        if self._dynamic:
            if time.time() - self._start_time >= 0.5:
                if self._text.strip():
                    text = self.text()
                    s = text.strip(self._text)
                    c = len(s)
                    if c == 0:
                        a = self._loading_flag * 1
                    elif c == 1:
                        a = self._loading_flag * 2
                    elif c == 2:
                        a = self._loading_flag * 3
                    elif c == 3:
                        a = ''
                    self.setText(f'{self._text}{a}')
                    self._start_time = time.time()

    def closeEvent(self, event):
        if self.movie:
            self.movie.stop()
        super().closeEvent(event)


class ScrollLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, *a, **kw):
        super(ScrollLabel, self).__init__(*a, **kw)
        self.startTimer(100)
        self.m_nCharWidth = 0
        self.m_nCurrentIndex = 0  # 文本起始x点
        self.m_nTextWidth = 0
        self.m_strText = ''
        self.m_strDrawText = ''

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        super().mousePressEvent(ev)
        if ev.button() == Qt.LeftButton:
            self.clicked.emit()

    def clear_text(self):
        self.clear()
        self.m_strDrawText = ''
        self.repaint()

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        if not self.text():
            self.m_strDrawText = ''
            self.update()
            return
        if self.m_strText != self.text():
            self.m_strText = self.text()
            self.m_nCurrentIndex = 0
            self.m_nTextWidth = self.fontMetrics().width(self.m_strText)
        while (self.fontMetrics().width(self.m_strDrawText) < self.width() + self.m_nTextWidth):
            self.m_strDrawText += self.text()
        self.m_nCurrentIndex += 1
        if self.m_nCurrentIndex == self.m_nTextWidth:
            self.m_nCurrentIndex = 0
        self.update()

    def paintEvent(self, a0) -> None:
        painter = QPainter(self)
        rectText = self.rect()
        if self.fontMetrics().width(self.text()) >= rectText.width():
            rectText.setWidth(self.width() + self.m_nTextWidth)
            rectText.setX(-self.m_nCurrentIndex)
            painter.drawText(rectText, self.alignment(), self.m_strDrawText)
        else:
            super().paintEvent(a0)


class Loading(GifLabel):

    def _hook(self, target: QWidget, margin: int):
        def resize_event(this, event):
            ret = this.__class__.resizeEvent(this, event)
            self.setFixedSize(this.size() - QSize(margin * 2, margin * 2))
            self.move(margin, margin)
            return ret

        target.resizeEvent = MethodType(resize_event, target)

    @classmethod
    def load(cls, target: QWidget, margin=0):

        if getattr(target, '__hook_xx_loading__', None) is None:
            self = cls(target)
            self._hook(target, margin)
            self.setAlignment(Qt.AlignCenter)
            self._target = target
            target.__hook_xx_loading__ = self
            self.setFixedSize(target.size() - QSize(margin * 2, margin * 2))
            self.move(margin, margin)
            self.setGif(':/imgs/加载2.gif')
            self.raise_()
            self.show()
        else:
            self = target.__hook_xx_loading__
            self.setFixedSize(target.size())
            self.setGif(':/imgs/加载2.gif')
            self.raise_()
            self.show()

    @classmethod
    def end(cls, target: QWidget):
        if getattr(target, '__hook_xx_loading__', None) is not None:
            target.__hook_xx_loading__.removeGif('')
            target.__hook_xx_loading__.hide()


class Loading2(Loading):

    def _hook(self, target: QWidget, margin: int):
        def resize_event(this, event):
            ret = this.__class__.resizeEvent(this, event)
            self.setFixedWidth(30)
            self.setFixedHeight(min(target.height() - margin * 2, 30))
            # self.move((this.width() - 30) / 2, margin)
            return ret

        target.resizeEvent = MethodType(resize_event, target)

    @classmethod
    def end(cls, target: QWidget):
        target.setEnabled(True)
        if getattr(target, '__hook_xx_loading2__', None) is not None:
            target.__hook_xx_loading2__.removeGif('')
            target.__hook_xx_loading2__.hide()

    @classmethod
    def load(cls, target: QWidget, margin=2):
        if getattr(target, '__hook_xx_loading2__', None) is None:
            self = cls(target)
            self._hook(target, margin)
            self.setAlignment(Qt.AlignCenter)
            self._target = target
            target.__hook_xx_loading2__ = self
            self.setFixedWidth(30)
            self.setFixedHeight(min(target.height() - margin * 2, 30))
            self.move((target.width() - 30) / 2, margin)
            self.setGif(':/imgs/加载2.gif')
            self.setStyleSheet('background: transparent')
            self.raise_()
            self.show()
        else:
            self = target.__hook_xx_loading2__
            self.setFixedWidth(30)
            self.setFixedHeight(min(target.height() - margin * 2, 30))
            self.setGif(':/imgs/加载2.gif')
            self.raise_()
            self.show()
        target.setEnabled(False)


class Pop(QPushButton):
    thread_sig = pyqtSignal(str)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.setStyleSheet(
            'QPushButton{background:#B6B6B6;color:white; border: 1px solid #B6B6B6;border-radius:5px;font-family: 微软雅黑}')
        fm = self.fontMetrics()
        self.setFixedHeight(fm.height() * 2)
        self._close_flag = False
        self._time_id = None

    def _hook(self, target: QWidget):
        def resize_event(this, event):
            ret = this.__class__.resizeEvent(this, event)
            target_size = this.size()
            pop_size = self.size()
            delta = (target_size - pop_size) / 2
            self.move(delta.width(), delta.height())
            return ret

        target.resizeEvent = MethodType(resize_event, target)

    def timerEvent(self, e) -> None:
        ret = super().timerEvent(e)
        if self._time_id is not None:
            self.killTimer(self._time_id)
            self._time_id = None
        self.close()
        return ret

    @classmethod
    def display(cls, text: str, target: QWidget, timeout: int = 4000):

        if getattr(target, '__hook_xx_pop__', None) is None:
            self = cls(target)
            self._hook(target)
            self.setText(text)
            fm = self.fontMetrics()
            self._target = target
            target.__hook_xx_pop__ = self
            self.setFixedWidth(fm.width(self.text()) + 20)
            self.setFixedHeight(fm.height() * 2)
            delta = (target.size() - self.size()) / 2
            self.move(delta.width(), delta.height())
            self.raise_()
            self.show()
            self._time_id = self.startTimer(timeout)

        else:
            self = target.__hook_xx_pop__
            fm = self.fontMetrics()
            # self.setFixedWidth(self.fontMetrics().width(self.text()) + 20)
            # self.setFixedHeight(fm.height() * 2)
            if self._time_id is not None:
                self.killTimer(self._time_id)
            self.raise_()
            self.show()
            self._time_id = self.startTimer(timeout)

    @classmethod
    def end(cls, target: QWidget):
        if getattr(target, '__hook_xx_pop__', None) is not None:
            target.__hook_xx_pop__.hide()


class Message(QDialog):
    _instances = set()

    def _get_mask(self, radius=5) -> QBitmap:
        bitmap = QBitmap(self.size())
        bitmap.fill(Qt.color0)
        painter = QPainter(bitmap)
        # painter.setRenderHint(QPainter.Antialiasing, True)
        # painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.HighQualityAntialiasing,
                               True)
        painter.setPen(Qt.transparent)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        painter.fillPath(path, Qt.color1)
        return bitmap

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.icon_label = QPushButton()
        self.icon_label.setStyleSheet("border:none")
        self.icon_label.setFixedWidth(18)
        self.icon_label.setFixedHeight(18)

        self.label = QLabel()
        self.label.setStyleSheet("border:none;font-family:微软雅黑")
        self.label.setAlignment(Qt.AlignCenter)
        self._timer = None
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 10, 10, 10)
        lay.addWidget(self.icon_label, 0)
        lay.addWidget(self.label, 1)
        self.setStyleSheet(
            "border: 1px solid lightgray;border-radius: 5px; background-color:white"
        )
        desktop = QApplication.desktop()
        fm = self.label.fontMetrics()
        label_height = fm.height()
        self.label.setFixedHeight(label_height)
        self._w = desktop.width()
        self._call_back = None

    def fwidth(self, msg: str):
        fm = self.label.fontMetrics()
        width = fm.width(msg)
        return width + 40 + self.icon_label.width()

    def _show(self, type: Literal["show", "exec_"] = "show", target: QWidget = None, center=None):
        height = self.height()
        count = len(self._instances)
        padding = 4
        self._instances.add(self)
        show_height = height * count + padding * count
        if target is not None:
            w = (self.parent().width() - self.width()) / 2
            # self.move(w, 3)
            self.move(w, show_height)
            self.raise_()
            if type == "show":
                self.show()
            else:
                self.exec_()
        else:
            desk = QApplication.desktop().size()
            size = self.size()
            s = (desk - size) / 2
            if center is None:
                h = 15 + show_height
            elif center == True:
                h = s.height()
            elif isinstance(center, (int, float)):
                h = int(center) + show_height
            self.move(s.width(), h)
            self.setMask(self._get_mask())
            self.raise_()
            self.show()

    def timerEvent(self, a0: "QTimerEvent") -> None:
        super().timerEvent(a0)
        if self._timer is not None:
            self.killTimer(self._timer)
            self.close()

    def close(self) -> bool:
        super().close()
        try:
            self._instances.remove(self)
        except:
            pass
        if self._call_back:
            self._call_back()

    @classmethod
    def info(cls, msg: str, target: QWidget = None, duration: int = 1500, type: Literal["show", "exec_"] = "show",
             center: Union[bool, int] = None):
        w = cls(target)
        icon = QIcon(":/imgs/成功.svg")
        h = w.label.height() + 20
        icon_size = (h - 20) + 4
        w.icon_label.setIcon(icon)
        w.icon_label.setIconSize(QSize(icon_size, icon_size))
        w.icon_label.setFixedSize(QSize(icon_size, icon_size))
        w.label.setText(msg)
        w.setFixedWidth(w.fwidth(msg))
        w.setFixedHeight(h)
        w._timer = w.startTimer(duration)
        w._show(type, target, center)

    @classmethod
    def warn(cls, msg: str, target: QWidget = None, duration: int = 1500, type: Literal["show", "exec_"] = "show",
             call_back=None, center: Union[bool, int] = None):
        w = cls(target)
        w._call_back = call_back
        icon = QIcon(":/imgs/失败.svg")
        h = w.label.height() + 20
        icon_size = (h - 20) + 4
        w.icon_label.setIcon(icon)
        w.icon_label.setIconSize(QSize(icon_size, icon_size))
        w.icon_label.setFixedSize(QSize(icon_size, icon_size))
        w.label.setText(msg)
        w.setFixedWidth(w.fwidth(msg))
        w.setFixedHeight(h)
        w._timer = w.startTimer(duration)
        w._show(type, target, center)


class Toast(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._font = QFont('微软雅黑', 9)
        self._text = None
        self._target = None
        self._max_width = 100
        self._padding = 10
        self._back_color = QColor('#404040')
        self._text_color = QColor(Qt.white)

        self._cursor_x = None
        self._place = 't'
        self._cursor_w = 10
        self._cursor_h = 5

        self._keep = False

        self.installEventFilter(self)

    def _text_height(self, text: str):
        fm = QFontMetrics(self._font)
        lines = []
        k = 0
        length = len(text)
        raw = text
        for index, i in enumerate(range(length)):
            l = text[:i - k]
            if fm.width(l) <= self._max_width:
                pass
            else:
                lines.append(''.join(l))
                text = text[i - k:]
                k = len(l)
        l = len(lines)
        last = raw.replace(''.join(lines), '')
        lines.append(last)
        return l, lines

    def eventFilter(self, a0, a1) -> bool:
        if a1.type() == QEvent.WindowDeactivate:
            if not self._keep:
                if self._target is not None:
                    delattr(self._target, '__0xxxmake_text_from_toastxxx0__')
                self.close()
        return QDialog.eventFilter(self, a0, a1)

    def paintEvent(self, a0: 'QPaintEvent') -> None:
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.TextAntialiasing, True)
        painter.setPen(self._back_color)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height() - 5, 3, 3)

        x1 = QPoint(self.width() / 2 - 5, self.height() - 5)
        x2 = QPoint(self.width() / 2 + 5, self.height() - 5)
        x3 = QPoint(self.width() / 2, self.height())
        path.addPolygon(QPolygonF([x1, x2, x3]))

        painter.fillPath(path, self._back_color)

        # if self._text:
        #     painter.setPen(self._text_color)
        #     painter.setFont(self._font)
        #     rect = QRect(self._padding, self._padding, self.width(
        #     ) - 2 * self._padding, self.height() - 2 * self._padding - 5)
        #     # painter.drawRect(QRectF(rect))
        #     painter.drawText(rect, Qt.AlignLeft, self._text)

    @classmethod
    def make_text(cls, text: str, target: QWidget,
                  text_color=None, back_color=None,
                  width=100, place: Literal['l', 'r', 't', 'b'] = 't',
                  keep=False):

        self = cls()
        self._keep = keep
        self._max_width = width
        self._place = place

        if text_color is not None:
            self._text_color = QColor(text_color)
        if back_color is not None:
            self._back_color = QColor(back_color)

        fm = QFontMetrics(self._font)
        size, lines = self._text_height(text)

        self.label = QLabel(self)
        # self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.label.setFont(self._font)
        self.label.setStyleSheet(
            f'border:none;background:transparent;color: {self._text_color.name()};')

        self._text = '\n'.join(lines)

        height = fm.height() * size + fm.lineSpacing()
        width = self._max_width + self._padding * 2 + 2

        self.setFixedWidth(width + fm.width(' ') * 1.5)
        self.setFixedHeight(height + self._padding * 2 + 5)

        self.label.move(self._padding, self._padding)
        self.label.setFixedWidth(self.width() - self._padding * 2)
        self.label.setFixedHeight(self.height() - self._padding * 2 - 5)
        self.label.setText(''.join(lines))
        self.label.setWordWrap(True)

        self._target = target
        setattr(target, '__0xxxmake_text_from_toastxxx0__', self)
        p1 = target.mapToGlobal(QPoint(target.width() / 2, 0))
        self.move(p1 - QPoint(self.width() / 2, self.height()))
        self.raise_()
        self.show()
        return self


class Modal(object):
    # 遮罩颜色
    mask_color = QColor(200, 200, 200, 70)

    @classmethod
    def _hook_parent(cls, obj: QWidget):
        def add_shadow(pixmap: QPixmap):
            painter = QPainter()
            painter.begin(pixmap)
            painter.fillRect(pixmap.rect(), cls.mask_color)
            painter.end()

        def _leave_focus(this):
            pixmap = this.grab()
            add_shadow(pixmap)
            this.__focus_label__.setFixedSize(pixmap.size())
            this.__focus_label__.setPixmap(pixmap)
            this.__focus_label__.raise_()
            this.__focus_label__.show()

        def _in_focus(this):
            this.__focus_label__.hide()

        # 遮罩绘制
        label = QLabel(obj)
        label.setStyleSheet('border:none')
        label.hide()
        obj.__focus_label__ = label
        # obj.closeEvent = MethodType(closeEvent, obj)
        obj._leave_focus = MethodType(_leave_focus, obj)
        obj._in_focus = MethodType(_in_focus, obj)

    @classmethod
    def _hook_modal(cls, obj: QWidget):
        def closeEvent(this, event):
            this.__class__.closeEvent(this, event)
            this.parent()._in_focus()

        obj.closeEvent = MethodType(closeEvent, obj)

    @classmethod
    def show(cls, title: str, show_content: QWidget, parent: QWidget,
             bar_color=QColor('#426BDD'),
             text_color=Qt.white,
             back_color=Qt.white):
        t = TitleWidget(title, show_content, bar_color, parent)
        cls._hook_modal(t)
        cls._hook_parent(parent)

        t.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        t.setWindowModality(Qt.WindowModal)
        t.setTextColor(text_color)
        t.hide_titlebar_all()
        btn = t.close_btn(
            'QPushButton{color:%s;border:none;background:transparent}' % QColor(text_color).name())
        t.addTitleWidget(btn)
        t.resize(show_content.size())
        t.setStyleSheet('TitleWidget{background:%s}' %
                        QColor(back_color).name())
        desk = QApplication.desktop().size()
        si = show_content.size()
        x = (desk - si) / 2
        t.move(QPoint(x.width(), x.height()))
        parent._leave_focus()
        t.show()


class Confirm(QDialog):

    @classmethod
    def msg(cls, title: str, target: QWidget, ok=None, cancel=None):
        def _wraper_ok():
            dia.close()
            if ok:
                ok()

        def _wraper_cancel():
            dia.close()
            if cancel:
                cancel()

        dia = QDialog(target)
        dia.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dia.setStyleSheet(
            'QDialog{background: white;border:1px solid lightgray}')

        lay = QVBoxLayout(dia)
        frame = QFrame()
        f_lay = QHBoxLayout(frame)
        info_btn = QPushButton()
        info_btn.setStyleSheet('border:none')
        info_btn.setIcon(QIcon(':/new/问号2.svg'))
        info_btn.setIconSize(QSize(25, 25))
        f_lay.addWidget(info_btn, 0)
        info_label = QLabel()
        info_label.setStyleSheet('border:none;font-family: 微软雅黑')
        f_lay.addWidget(info_label, 1)
        info_label.setText(title)

        btn_frames = QFrame()
        btn_lay = QHBoxLayout(btn_frames)
        btn_lay.addSpacerItem(QSpacerItem(
            20000, 20, hPolicy=QSizePolicy.Expanding))

        ok_btn = QPushButton('确认', clicked=_wraper_ok)
        cancel_btn = QPushButton('取消', clicked=_wraper_cancel)
        ok_btn.setStyleSheet(
            'QPushButton{font-family:微软雅黑;background: #40A9FF;color:white;border:1px solid #40A9FF;border-radius:3px}'
            'QPushButton:hover{background: rgb(24,144,255);border:1px solid rgb(24,144,255)}')
        cancel_btn.setStyleSheet(
            'font-family: 微软雅黑; background: white;border:1px solid gray;border-radius:3px')

        ok_btn.setFixedWidth(ok_btn.fontMetrics().width('测') * 4)
        ok_btn.setFixedHeight(ok_btn.fontMetrics().height() * 2)
        cancel_btn.setFixedSize(ok_btn.size())
        ok_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setCursor(Qt.PointingHandCursor)

        btn_lay.addWidget(cancel_btn)
        btn_lay.addWidget(ok_btn)

        lay.addWidget(frame, 1)
        lay.addWidget(btn_frames, 0)
        flag = (target.size() - dia.size()) / 2
        dia.setMaximumWidth(300)
        dia.exec_()
        dia.move(flag.width(), flag.height())


class Alerts(QDialog):

    def __init__(self, target: QWidget = None) -> None:
        super().__init__(target)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Dialog | Qt.WindowStaysOnTopHint)
        lay = QGridLayout(self)

        icon = QPushButton()
        icon.setStyleSheet('border:none;background:transparent')
        icon.setIcon(QIcon(':/feedback/警告 (2).svg'))
        lay.addWidget(icon, 0, 0)

        title = QLabel()
        title.setStyleSheet('font-family:微软雅黑;font-weight:bold')
        lay.addWidget(title, 0, 1)

        content = QLabel()
        content = QLabel()
        content.setStyleSheet('font-family:微软雅黑;color: gray')
        lay.addWidget(content, 1, 1)

        self.title_label = title
        self.content_label = content
        self.icon = icon

        self.setMaximumWidth(300)
        self.time_id = None

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        ret = super().timerEvent(a0)
        if self.time_id is not None:
            self.killTimer(self.time_id)
            self.close()

    @classmethod
    def info(cls, title: str, content: str, target: QWidget = None, duration=3000):
        dialog = cls(target)
        dialog.setStyleSheet(
            'QDialog{border:1px solid #91D5FF;background: #E6F7FF;border-radius:3px}')
        dialog.title_label.setText(title)
        dialog.content_label.setText(content)
        dialog.time_id = dialog.startTimer(duration)
        dialog.raise_()
        dialog.exec_()

    @classmethod
    def warn(cls, title: str, content: str, target: QWidget = None, duration=3000):
        dialog = cls(target)
        dialog.icon.setIcon(QIcon(':/feedback/警告 (3).svg'))
        dialog.setStyleSheet(
            'QDialog{border:1px solid #FFE58F;background: #FFFBE6;border-radius:3px}')
        dialog.title_label.setText(title)
        dialog.content_label.setText(content)
        dialog.time_id = dialog.startTimer(duration)
        dialog.raise_()
        dialog.exec_()

    @classmethod
    def error(cls, title: str, content: str, target: QWidget = None, duration=3000):
        dialog = cls(target)
        dialog.icon.setIcon(QIcon(':/feedback/警告-红.svg'))
        dialog.setStyleSheet(
            'QDialog{border:1px solid #FFA39E;background: #FFF1F0;border-radius:3px}')
        dialog.title_label.setText(title)
        dialog.content_label.setText(content)
        dialog.time_id = dialog.startTimer(duration)
        dialog.raise_()
        dialog.exec_()


class NoData(QWidget):
    def __init__(self, *a, **kw):
        super(NoData, self).__init__(*a, **kw)
        self._lay = QHBoxLayout(self)
        self._label = QLabel(self)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setFixedSize(QSize(60, 60))
        self._lay.addWidget(self._label)

    @classmethod
    def display(cls, target: QWidget, image: Union[bytes, str, QPixmap] = None):
        def hook(this, event):
            this.__class__.resizeEvent(this, event)


class RotateBtn(QPushButton):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._pixmap: QPixmap = None
        self._timer = None
        self._rorate = 0

    def setRotatePixmap(self, source: Union[str, bytes, QPixmap], rotate=15, freq=100):
        if isinstance(source, bytes):
            pixmap = QPixmap()
            pixmap.loadFromData(source)
        else:
            pixmap = QPixmap(source)
        self._pixmap = pixmap  # .scaled(18,18,transformMode=Qt.SmoothTransformation)
        self.startTimer(freq)

    def timerEvent(self, a0: 'QTimerEvent') -> None:
        super().timerEvent(a0)
        if self._pixmap is not None:
            self._rorate += 10
            transform = QTransform()
            t = transform.rotate(self._rorate)
            pixmap_rotated = self._pixmap.transformed(t, Qt.SmoothTransformation)
            self.setIconSize(QSize(18, 18))
            self.setIcon(QIcon(pixmap_rotated))

    def _get_rotate_picture(self):
        pixmap = QPixmap(self._pixmap.size())
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setTransform(QTransform().rotate(self._rorate))
        painter.drawPixmap(pixmap.rect(), pixmap)
        return pixmap


# bug fix
class Toast2(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self._target = None
        self._padding = 10
        self._back_color = QColor('#404040')
        self._text_color = QColor(Qt.white)
        self.setFont(QFont('微软雅黑', 9))
        self.setWordWrap(True)
        self.setMargin(self._padding)
        self.setStyleSheet(
            f'color: white; border:none;background: transparent')
        self.installEventFilter(self)

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a1.type() == QEvent.WindowDeactivate:
            if self._target is not None:
                delattr(self._target, '__0xxxmake_text_from_toastxxx0__')
            self.close()
        return QLabel.eventFilter(self, a0, a1)

    def paintEvent(self, a0) -> None:
        super().paintEvent(a0)
        painter = QPainter(self)
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 3, 3)

        x1 = QPoint(self.width() / 2 - 5, self.height() - 5)
        x2 = QPoint(self.width() / 2 + 5, self.height() - 5)
        x3 = QPoint(self.width() / 2, self.height())
        path.addPolygon(QPolygonF([x1, x2, x3]))
        # painter.fillPath(path, self._back_color)

    def _text_height(self, text: str, width):
        fm = self.fontMetrics()
        lines = []
        k = 0
        length = len(text)
        raw = text
        for index, i in enumerate(range(length)):
            l = text[:i - k]
            if fm.width(l) < width:
                pass
            else:
                lines.append(''.join(l))
                text = text[i - k:]
                k = len(l)
        l = len(lines)
        last = raw.replace(''.join(lines), '')
        lines.append(last)
        return l, lines

    @classmethod
    def make_text(cls, text, target, width=200, back_color=None):
        try:
            self = cls()
            l, _ = self._text_height(text, width)
            fm = self.fontMetrics()
            self.setText(text)
            self = cls()
            h = fm.height() * l + fm.lineSpacing()
            self.setFixedWidth(width + fm.width('想') * 2)
            self.setFixedHeight(h + self._padding * 2)
            self._target = target
            setattr(target, '__0xxxmake_text_from_toastxxx0__', self)
            p1 = target.mapToGlobal(QPoint(target.width() / 2, 0))
            self.move(p1 - QPoint(self.width() / 2, self.height()))
            self.show()
        except:
            import traceback
            traceback.print_exc()


class TqdmLabel(QLabel):
    def write(self, text):
        self.setText(text)

    def flush(self):
        pass


class Tqdm(object):

    def __init__(self, total, initial, desc, unit='B', unit_scale=True, file=None, freq=0.3):
        self.total = total
        self.initial = initial
        self.desc = desc
        self.unit = unit
        self.unit_scale = unit_scale
        self.file = file or sys.stdout
        self.freq = freq

        self._disabled = False
        self._delta = 0
        self._start_time = None
        self._update_time = None
        self._lock = threading.Lock()

    def _hum_convert(self, value: int) -> Tuple[float, str]:
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        size = 1024.0
        for i in range(len(units)):
            if (value / size) < 1:
                return round(value, 1), units[i]
            value = value / size

    def close(self):
        self._disabled = True

    def update(self, v):
        with self._lock:
            try:
                if not self._disabled:
                    self.initial += v

                    if self._update_time is None:
                        self._update_time = self._start_time = time.time()

                    if time.time() - self._update_time >= self.freq:
                        fmt = format(self.initial / self.total * 100, '.1f')
                        f1, f2 = fmt.split('.')
                        f1 = f1.rjust(3, ' ')
                        fmt = f1 + '.' + f2
                        cur, u1 = self._hum_convert(self.initial)
                        total, u2 = self._hum_convert(self.total)
                        es = int(time.time() - self._start_time)
                        msg = f'{self.desc}: {fmt}% | {cur}{u1}/{total}{u2} {dt(seconds=es)}'
                        rate_, rate_unit_ = self._hum_convert(
                            self._delta / self.freq)
                        rate = f'{rate_}{rate_unit_}/s'
                        self._update_time = time.time()
                        self._delta = 0
                        self.file.write(msg + f' {rate}')
                        self.file.flush()
                    else:
                        self._delta += v
                        if self.initial == self.total:
                            try:
                                total, u2 = self._hum_convert(self.total)
                                es = int(time.time() - self._start_time)
                                msg = f'{self.desc}: 100% | {total}{u2}/{total}{u2} {dt(seconds=es)}'
                                self.file.write(msg)
                                self.file.flush()
                            except:
                                pass
            except:
                pass


# 异步多线程
class BackgroundWorker(QObject):
    done_sig = pyqtSignal(dict)

    sync_enter_sig = pyqtSignal(object)
    sync_exit_sig = pyqtSignal(object)
    sync_lock = threading.Event()
    sync_enter = None
    sync_exit = None

    class _AsyncThread(QThread):
        def __init__(self, loop) -> None:
            super().__init__()
            self.async_loop = loop

        def run(self):
            asyncio.set_event_loop(self.async_loop)
            self.async_loop.run_forever()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.async_loop = asyncio.new_event_loop()
        self._thread = self._AsyncThread(self.async_loop)
        self.moveToThread(self._thread)
        self._thread.start()

        self.done_sig.connect(self._back_ground_call)

        self.sync_enter_sig.connect(self._call_sync_enter)
        self.sync_exit_sig.connect(self._call_sync_exit)

    @classmethod
    def _call_sync_enter(cls, recevied: Generator):
        # cls.lock.set()
        cls.sync_enter = staticmethod(next(recevied))
        print('in enter ', cls.sync_enter,
              threading.current_thread() is threading.main_thread())
        cls.sync_lock.set()

    @classmethod
    def _call_sync_exit(cls, recevied: Tuple[Generator, Any]):
        try:
            print('in exit', threading.current_thread()
                  is threading.main_thread())
            recevied[0].send(recevied[1])
        except StopIteration:
            pass

    @classmethod
    def _back_ground_call(cls, res: dict):
        state = res.get("state")
        call_back = res.get('call_back')
        err_back = res.get('err_back')
        error = res.get('error')
        if state:
            if call_back:
                call_back()
        else:
            if err_back:
                err_back(error)

    def add_task(self, func, args=(), kwargs={}, call_back=None, err_back=None):
        self.async_loop.call_soon_threadsafe(
            self._sync_wrapper(
                func, *args, **kwargs, call_back=call_back, err_back=err_back
            )
        )

    def _sync_wrapper(self, func, *args, call_back=None, err_back=None):

        def inner():
            try:
                res = func(*args)
                is_generator = isgenerator(res)
                ret = None
                if is_generator:
                    self.sync_enter_sig.emit(res)
                    self.sync_lock.wait()
                    ret = self.sync_enter(*args)

                def call():
                    return call_back(res) if call_back else None

                self.done_sig.emit(
                    {
                        "state": True,
                        "ret": ret if is_generator else res,
                        "func": func.__name__,
                        "call_back": call,
                        "err_back": err_back,
                        "error": None,
                    }
                )
                if is_generator:
                    self.sync_exit_sig.emit((res, ret))
            except Exception as e:
                self.done_sig.emit(
                    {
                        "state": False,
                        "ret": None,
                        "func": func.__name__,
                        "call_back": call_back,
                        "err_back": err_back,
                        "error": e,
                    }
                )
                try:
                    if is_generator:
                        self.sync_exit_sig.emit((res, e))
                except:
                    pass

        return inner

    def add_coro(self, coro, call_back=None, err_back=None):
        asyncio.run_coroutine_threadsafe(
            self._async_wrapper(
                coro, call_back, err_back=err_back), self.async_loop
        )

    async def _async_wrapper(self, coro, call_back=None, err_back=None):
        try:
            res = await coro

            def call():
                return call_back(res) if call_back else None

            self.done_sig.emit(
                {
                    "state": True,
                    "ret": res,
                    "func": coro.__name__,
                    "call_back": call,
                    "err_back": err_back,
                    "error": None
                }
            )
        except Exception as e:
            self.done_sig.emit(
                {
                    "state": False,
                    "ret": None,
                    "func": coro.__name__,
                    "call_back": call_back,
                    "err_back": err_back,
                    "error": e
                }
            )


class DownLoader(BackgroundWorker):
    _instance = None
    _sig = pyqtSignal(int)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def down_load(self, url: str, dst: str, call_back=None, err_back=None, out_put=None, timeout=15, logger=None):
        self.add_coro(self._down_from_url(url, dst, out_put,
                                          timeout, logger), call_back, err_back)

    async def _down_from_url(self, url, dst, output: TqdmLabel = None, timeout=15, logger=None):
        # from tqdm import tqdm
        async def fetch(session, url, dst, pbar=None, headers=None):
            if headers:
                if Path(dst).exists():
                    mode = 'ab'
                else:
                    mode = 'wb'
                async with session.get(url, headers=headers) as req:
                    with open(dst, mode) as f:
                        while True:
                            chunk = await req.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                            pbar.update(1024)
                    pbar.close()
            else:
                async with session.get(url) as req:
                    return req

        while True:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                    req = await fetch(session, url, dst)
                    file_size = int(req.headers.get('content-length'))
                    if Path(dst).exists():
                        first_byte = Path(dst).stat().st_size
                    else:
                        first_byte = 0
                    header = {'Range': f'bytes={first_byte}-{file_size}'}
                    if output is not None:
                        self._pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, file=output,
                                          desc='已下载',
                                          bar_format='{desc}:{percentage:3.0f}% | {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]')
                    else:
                        self._pbar = tqdm(total=file_size, initial=first_byte, unit='B', unit_scale=True, desc=dst,
                                          )
                    await fetch(session, url, dst, self._pbar, header)
            except Exception:
                if logger:
                    logger.warn(f'retry download')
                if output is not None:
                    text = output.text()
                else:
                    text = None
                self._pbar.close()
                if text is not None:
                    output.setText(text)
                continue
            else:
                break

    def down_loadEx(self, url, dst, call_back=None, err_back=None, timeout=15, logger=None, cons=10,
                    output: TqdmLabel = None, show_message: bool = True):
        self.add_coro(self._down_from_url_range(url, dst, timeout,
                                                cons, logger, output, show_message), call_back, err_back)

    async def _down_from_url_range(self, url: str, dst: str, timeout: int, threads: int, logger=None,
                                   output: TqdmLabel = None, show_message: bool = True):
        # from tqdm import tqdm

        def update_tqdm(v):
            self._pbar_ex.update(v)

        def _split(length: int, threads: int, dst: str) -> List:
            count = length // threads
            ret = []
            for i in range(threads - 1):
                ds = f'{dst}.download_{i}'
                file_range = count * i, count * (i + 1) - 1
                ret.append([ds, file_range, {'downsize': 0}])
            ret.append([f'{dst}.download_{threads - 1}',
                        (count * (threads - 1), length), {'downsize': 0}])
            return ret

        async def fetch(session: aiohttp.ClientSession, url: str, dst: str, headers: dict = None,
                        is_modified: bool = False):
            if headers:
                if Path(dst).exists():
                    if is_modified:
                        mode = 'wb'
                    else:
                        mode = 'ab'
                else:
                    mode = 'wb'
                try:
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=timeout)) as req:
                        with open(dst, mode) as f:
                            while True:
                                chunk = await req.content.read(1024)
                                if not chunk:
                                    break
                                f.write(chunk)
                                self._sig.emit(len(chunk))
                except:
                    raise
            else:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as req:
                    return req

        async def _down_load_range(url: str, dst: str, file_range: Tuple, is_modified: bool,
                                   sess: aiohttp.ClientSession):
            _is_modified = is_modified
            while True:
                try:
                    if Path(dst).exists():
                        first_byte = Path(dst).stat().st_size
                    else:
                        first_byte = 0
                    s, e = file_range
                    if first_byte < e - s + 1:
                        reqs = s + first_byte, e
                        header = {'Range': f'bytes={reqs[0]}-{reqs[1]}'}
                        await fetch(sess, url, dst, headers=header,
                                    is_modified=_is_modified)
                except:
                    _is_modified = False
                    continue
                else:
                    break
            return Path(dst)

        try:
            async with aiohttp.ClientSession() as sess:
                is_modified = False
                req = await fetch(sess, url, dst)
                length = int(req.headers.get('content-length'))
                last_modified = req.headers.get('last-modified')

                fname = Path(dst).name
                ep = Path(dst).parent.joinpath(f'{fname}.download_info')

                if ep.exists():
                    text = ep.read_text(encoding='utf8').strip()
                    if text != last_modified.strip():
                        is_modified = True
                else:
                    ep.write_text(last_modified.strip(), encoding='utf8')
                    is_modified = True

                inits = 0
                for ef in Path(dst).parent.iterdir():
                    if ef.__str__().startswith(f'{dst}.download_'):
                        inits += ef.stat().st_size

                # self._pbar_ex = tqdm(total=length, initial=inits, unit='B', unit_scale=True,
                #                      desc='已下载', file=output,
                #                      bar_format='{desc}:{percentage:3.0f}% | {n_fmt}/{total_fmt} [{elapsed} < {remaining}, {rate_fmt}{postfix}]')

                if show_message:
                    self._pbar_ex = Tqdm(
                        length, inits, desc='已下载', file=output)
                    self._sig.connect(update_tqdm)

                tasks = []
                task_args = _split(length, threads, dst)
                for args in task_args:
                    ds, file_range, down_size = args
                    coro = _down_load_range(
                        url, ds, file_range, is_modified, sess)
                    tasks.append(coro)

                results = await asyncio.gather(*tasks, loop=self.async_loop)

                with open(dst, 'wb') as f:
                    for pf in results:
                        f.write(pf.read_bytes())

                for pf in results:
                    try:
                        pf.unlink()
                    except:
                        pass

                try:
                    ep.unlink()
                except:
                    pass

                if show_message:
                    self._sig.disconnect(update_tqdm)
                    self._pbar_ex.close()
                    self._pbar_ex = None

                return dst

        except:
            if logger:
                logger.warn('error', exc_info=True)
            raise


class GrabWidget(QWidget):
    show_sig = pyqtSignal(QListWidgetItem)
    select_sig = pyqtSignal(QListWidgetItem)
    delete_sig = pyqtSignal(QListWidgetItem)

    class _HoverLabel(QLabel):
        show_sig = pyqtSignal(QListWidgetItem)
        select_sig = pyqtSignal(QListWidgetItem)
        delete_sig = pyqtSignal(QListWidgetItem)

        def __init__(self, parent, type: Literal["grab", "file"] = "grab"):
            super().__init__(parent)
            self._enter = False
            self.type = type
            self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.setStyleSheet('font-family: 微软雅黑;border:none')

        def resize(self, a0) -> None:
            super().resizeEvent(a0)
            # w, h = self.width(), self.height()

        def enterEvent(self, a0) -> None:
            super().enterEvent(a0)

        def leaveEvent(self, a0) -> None:
            super().leaveEvent(a0)

    def __init__(self, item: QListWidgetItem) -> None:
        super().__init__()
        self._item = item
        self._text = ""
        self._enter = False

        but_frame = QFrame()
        but_frame.setStyleSheet(
            'QFrame{border:none;background-color:transparent}')
        but_lay = QHBoxLayout(but_frame)
        but_lay.setSpacing(2)
        but_lay.setContentsMargins(1, 1, 1, 1)
        but_lay.addSpacerItem(QSpacerItem(
            20, 20, hPolicy=QSizePolicy.Expanding))

        button = QPushButton(self)
        # button.setIcon(QIcon(":/imgs/预览.svg"))
        button.setFixedSize(QSize(16, 16))
        btn_style = "QPushButton{border:none; background-color: transparent; border-image: url(:/imgs/预览.svg)}" \
                    "QPushButton:hover{border-image: url(:/imgs/预览(1).svg);}"
        button.setStyleSheet(btn_style)
        button.setToolTip("查看")
        self.button = button
        self.button.setCursor(QCursor(Qt.PointingHandCursor))
        self.button.clicked.connect(
            lambda: self.show_sig.emit(self._item)
        )

        select_button = QPushButton(self)
        select_button.setFixedSize(QSize(16, 16))
        # select_button.setIcon(QIcon(":/imgs/替换图片.svg"))
        btn_style = "QPushButton{border:none; background-color: transparent; border-image: url(:/imgs/替换图片.svg)}" \
                    "QPushButton:hover{border-image: url(:/imgs/替换图片(1).svg)}"
        select_button.setStyleSheet(btn_style)
        self.select_button = select_button
        self.select_button.clicked.connect(
            lambda: self.select_sig.emit(self._item)
        )
        select_button.setToolTip("重选")
        self.select_button.setCursor(QCursor(Qt.PointingHandCursor))

        delete_button = QPushButton(self)
        # delete_button.setIcon(QIcon(":/imgs/移除(1).svg"))
        delete_button.setFixedSize(QSize(16, 16))
        btn_style = "QPushButton{border:none; background-color: transparent;border-image: url(:/imgs/移除(1).svg)}" \
                    "QPushButton:hover{border-image: url(:/imgs/移除.svg)}"
        delete_button.setStyleSheet(btn_style)
        delete_button.setToolTip("移除")
        self.delete_button = delete_button
        self.delete_button.clicked.connect(
            lambda: self.delete_sig.emit(self._item)
        )
        self.delete_button.setCursor(QCursor(Qt.PointingHandCursor))

        but_lay.addWidget(self.button)
        but_lay.addWidget(self.select_button)
        but_lay.addWidget(self.delete_button)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(1)

        label = QLabel()
        label.setAlignment(Qt.AlignCenter)
        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        label.setStyleSheet("border:none;")
        label.setScaledContents(True)
        self.label = label

        lay.addWidget(but_frame)
        lay.addWidget(label, 1)
        self.setStyleSheet('border:none')

    def set_text(self, text):
        pass

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        self.label.setMaximumWidth(self.width() - 4)

    def paintEvent(self, a0) -> None:
        super().paintEvent(a0)
        if self._enter:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            painter.setPen(Qt.lightGray)
            rect = QRectF(0, 0, self.width(), self.height())
            painter.drawRect(rect, )

    def enterEvent(self, a0) -> None:
        super().enterEvent(a0)
        self._enter = True
        self.update()

    def leaveEvent(self, a0) -> None:
        super().leaveEvent(a0)
        self._enter = False
        self.update()

    def get_pixmap_from_file(self) -> Optional[QPixmap]:
        desk_top = Path.home() / "Desktop"
        if desk_top.exists():
            dst = str(desk_top.absolute())
        else:
            dst = str(Path.cwd().absolute())
        file, _ = QFileDialog.getOpenFileName(
            self, "选择上传的图片", dst, "*.png;*.jpg;*.jpeg"
        )
        if file:
            pixmap = QPixmap(file)
            if not pixmap.isNull():
                return pixmap


class ShowPicWidget(QWidget):
    def __init__(self, pixmap: str, his_data: dict) -> None:
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        pixmap = QPixmap(pixmap)
        desk_top = QApplication.desktop().size()
        flag = pixmap.size() - desk_top
        if flag.width() > 0 or flag.height() > 0:
            pixmap = pixmap.scaled(
                desk_top * 3 / 4, transformMode=Qt.SmoothTransformation)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.label)
        self.label.setPixmap(pixmap)

        self.setWindowTitle(his_data.get("dd_number"))
        self.setWindowIcon(QIcon(":/imgs/图片查看.svg"))

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |
                            Qt.WindowCloseButtonHint)


def hook_windowDeactivate(target):
    def eventFilter(self, object: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.WindowDeactivate:
            self.close()
        return target.__class__.eventFilter(self, object, event)

    target.eventFilter = MethodType(eventFilter, target)
    target.installEventFilter(target)
    return target


class HorizonHeaderView(QHeaderView):
    search_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.table: QTableWidget = parent
        self.search_line = self.create_search()

    def create_search(self):
        def show_search():
            w = QLineEdit()
            hook_windowDeactivate(w)
            w.setStyleSheet(
                'font-family: 微软雅黑;border: 1px solid gray;border-radius:4px')
            w.setFixedHeight(w.fontMetrics().height() * 2.5)
            w.setPlaceholderText('请输入银行名称')
            w.setClearButtonEnabled(True)
            w.setMaximumWidth(150)
            w.setWindowFlags(Qt.FramelessWindowHint | Qt.Widget)
            w.textEdited.connect(self.search_signal)

            # l = QVBoxLayout(w)
            # l.setSpacing(0)
            # l.setContentsMargins(0, 0, 0, 0)
            #
            # listwidget = QListWidget()
            # listwidget.addItems(list('abcd'))
            #
            # l.addWidget(listwidget)
            p = widget.mapToGlobal(QPoint(0, widget.height()))

            self.w = w

            w.move(p)
            w.show()
            w.raise_()

        widget = QWidget(self)
        lay = QHBoxLayout(widget)
        lay.setSpacing(1)
        lay.setContentsMargins(0, 0, 0, 0)

        label = QLabel()
        label.setText('银行名')
        label.setStyleSheet('font-family: 微软雅黑;font-weight:bold')
        label.setAlignment(Qt.AlignCenter)

        btn = QPushButton()
        btn.setIcon(QIcon(':/imgs/搜索小.svg'))
        btn.setStyleSheet(
            'QPushButton{border:none}QPushButton:hover{background: lightgray};')
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(show_search)

        lay.addWidget(label, 1)
        lay.addWidget(btn, 0)

        return widget

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex: int) -> None:
        super(HorizonHeaderView, self).paintSection(
            painter, rect, logicalIndex)
        if logicalIndex == 1:
            self.search_line.setGeometry(rect)


class TableItemDelegate(QStyledItemDelegate):

    def paintFont(self) -> QFont:
        return QFont('等线', 11, QFont.Bold)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        sized = super().sizeHint(option, index)
        height = option.fontMetrics.height() + 10
        sized.setHeight(height)
        return sized

    def paint(self, painter: QPainter, option: QStyleOptionViewItem,
              index: QModelIndex) -> None:
        super().paint(painter, option, index)
        rect = option.rect  # 目标矩形
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setPen(Qt.red)
        painter.setFont(self.paintFont())
        painter.drawText(rect.adjusted(10, 10, -10, -10), Qt.AlignCenter,
                         option.text)
        painter.restore()

        # if option.state & QStyle.State_MouseOver:
        # pass
        # print(option.text)
        # if option.text:
        #     p_style = option.widget.style()
        #     document = QTextDocument()
        #     document.setHtml('<b><font color="red">GB</font></b>')
        #     paint_context = QAbstractTextDocumentLayout.PaintContext()
        #     text_rect = p_style.subElementRect(QStyle.SE_ItemViewItemText, option)
        #     painter.save()
        #     painter.translate(text_rect.topLeft())
        #     painter.setClipRect(text_rect.translated(-text_rect.topLeft()))
        #     document.documentLayout().draw(painter, paint_context)
        #     painter.restore()


################################# 自定义标题栏窗口 ########################################

class TitleBar(QWidget):
    # 窗口最小化信号
    windowMinimumed = pyqtSignal()
    # 窗口最大化信号
    windowMaximumed = pyqtSignal()
    # 窗口还原信号
    windowNormaled = pyqtSignal()
    # 窗口关闭信号
    windowClosed = pyqtSignal()
    # 窗口移动
    windowMoved = pyqtSignal(QPoint)
    # 鼠标点击
    mPressed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(TitleBar, self).__init__(*args, **kwargs)
        # 支持qss设置背景
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.mPos = None
        self.iconSize = 20  # 图标的默认大小
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        # 布局
        layout = QHBoxLayout(self, spacing=0)
        layout.setContentsMargins(10, 0, 0, 0)
        # 窗口图标
        self.iconLabel = QLabel(self)
        layout.addWidget(self.iconLabel)
        # 窗口标题
        self.titleLabel = QLabel(self)
        self.titleLabel.setAttribute(
            Qt.WA_TransparentForMouseEvents, True)  # 鼠标穿透,当前控件及其子控件均不响应鼠标事件
        self.titleLabel.setMargin(2)
        self.titleLabel.setFont(QFont('微软雅黑'))
        layout.addWidget(self.titleLabel)
        # 中间伸缩条
        layout.addSpacerItem(QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # 利用Webdings字体来显示图标
        font = self.font() or QFont()
        font.setFamily('Webdings')
        # 最小化按钮
        self.buttonMinimum = QPushButton(
            '0', self, clicked=self.windowMinimumed.emit, font=font, objectName='buttonMinimum')
        layout.addWidget(self.buttonMinimum)
        # 最大化/还原按钮
        self.buttonMaximum = QPushButton(
            '1', self, clicked=self.showMaximized, font=font, objectName='buttonMaximum')
        layout.addWidget(self.buttonMaximum)
        # 关闭按钮
        self.buttonClose = QPushButton(
            'r', self, clicked=self.windowClosed.emit, font=font, objectName='buttonClose')
        layout.addWidget(self.buttonClose)
        # 初始高度
        self.setHeight()
        self.setStyleSheet(Sh.StyleSheet)

        self.windowMinimumed.connect(self.mPressed)
        self.windowClosed.connect(self.mPressed)

    def addTitleWidget(self, widget, stretch=0, *, autoheight=True):
        lay: QHBoxLayout = self.layout()
        lay.insertWidget(3, widget, stretch=stretch)
        if autoheight:
            widget.setFixedHeight(self.height())
            widget.setMinimumWidth(self.height())

    def addLeftTitleWidget(self, widget, stretch=0, *, autoheight=True):
        lay: QHBoxLayout = self.layout()
        lay.insertWidget(2, widget, stretch=stretch)
        if autoheight:
            widget.setFixedHeight(self.height())
            widget.setMinimumWidth(self.height())

    def showMaximized(self):
        if self.buttonMaximum.text() == '1':
            # 最大化
            self.buttonMaximum.setText('2')
            self.windowMaximumed.emit()
        else:  # 还原
            self.buttonMaximum.setText('1')
            self.windowNormaled.emit()

    def setHeight(self, height=38):
        """设置标题栏高度"""
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        # 设置右边按钮的大小
        self.buttonMinimum.setMinimumSize(height, height)
        self.buttonMinimum.setMaximumSize(height, height)
        self.buttonMaximum.setMinimumSize(height, height)
        self.buttonMaximum.setMaximumSize(height, height)
        self.buttonClose.setMinimumSize(height, height)
        self.buttonClose.setMaximumSize(height, height)

    def setTitle(self, title):
        """设置标题"""
        self.titleLabel.setText(f'<b>{title}</b>')

    def setTitleStyle(self, styleSheet: str):
        self.titleLabel.setStyleSheet(styleSheet)

    def setIcon(self, icon):
        """设置图标"""
        self.iconLabel.setPixmap(icon.pixmap(self.iconSize, self.iconSize))

    def setIconSize(self, size):
        """设置图标大小"""
        self.iconSize = size

    def enterEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super(TitleBar, self).enterEvent(event)

    def mouseDoubleClickEvent(self, event):
        super(TitleBar, self).mouseDoubleClickEvent(event)
        # self.showMaximized()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.mPressed.emit()
        if event.button() == Qt.LeftButton:
            self.mPos = event.pos()
        event.accept()

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        self.mPos = None
        event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.mPos:
            self.windowMoved.emit(self.mapToGlobal(event.pos() - self.mPos))
        event.accept()


# 枚举左上右下以及四个定点
Left, Top, Right, Bottom, LeftTop, RightTop, LeftBottom, RightBottom = range(8)


class FramelessWindow(QWidget):
    # 四周边距
    Margins = 2

    CurSorMargins = 5

    def __init__(self, *args, **kwargs):
        super(FramelessWindow, self).__init__(*args, **kwargs)
        self._auto_resize = False
        self._pressed = False

        self.nestle_enable = False  # 贴靠
        self.moved = False  # flag

        self.border_color = Qt.lightGray

        self.Direction = None
        self.setMouseTracking(True)
        # 背景透明
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 无边框
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowMinimizeButtonHint)  # 隐藏边框
        # 鼠标跟踪
        self.setMouseTracking(True)
        # 布局
        layout = QVBoxLayout(self, spacing=0)
        # 预留边界用于实现无边框窗口调整大小
        layout.setContentsMargins(
            self.Margins, self.Margins, self.Margins, self.Margins)
        # 标题栏
        self.titleBar = TitleBar(self)
        layout.addWidget(self.titleBar)
        # 信号槽
        self.titleBar.windowMinimumed.connect(self.showMinimized)
        self.titleBar.windowMaximumed.connect(self.showMaximized)
        self.titleBar.windowNormaled.connect(self.showNormal)
        self.titleBar.windowClosed.connect(self.close)
        self.titleBar.windowMoved.connect(self.move)
        self.windowTitleChanged.connect(self.titleBar.setTitle)
        self.windowIconChanged.connect(self.titleBar.setIcon)

    def set_auto_resize(self, value: bool):
        self._auto_resize = value

    def addTitleWidget(self, widget, stretch=0, autoheight=True):
        self.titleBar.addTitleWidget(widget, stretch, autoheight=autoheight)

    def addLeftTitleWidget(self, widget, stretch=0, autoheight=True):
        self.titleBar.addLeftTitleWidget(
            widget, stretch, autoheight=autoheight)

    def setTitleBarHeight(self, height=38):
        """设置标题栏高度"""
        self.titleBar.setHeight(height)

    def setTitleBarColor(self, color):
        palatte = QPalette(self.titleBar.palette())
        palatte.setColor(QPalette.Background, QColor(color))
        # palatte.setColor(QPalette.Foreground, Qt.red)
        self.titleBar.setAutoFillBackground(True)
        self.titleBar.setPalette(palatte)
        self.titleBar.update()

    def barColor(self) -> QColor:
        palatte = self.titleBar.palette()
        return palatte.color(QPalette.Background)

    def barHeight(self):
        return self.titleBar.height() + self.Margins * 2

    def setIconSize(self, size):
        """设置图标的大小"""
        self.titleBar.setIconSize(size)

    def setWidget(self, widget):
        """设置自己的控件"""
        if hasattr(self, '_widget'):
            return
        self._widget = widget
        # 设置默认背景颜色,否则由于受到父窗口的影响导致透明
        self._widget.setAutoFillBackground(True)
        palette = self._widget.palette()
        palette.setColor(palette.Window, QColor(240, 240, 240))
        self._widget.setPalette(palette)
        self._widget.installEventFilter(self)
        self.layout().addWidget(self._widget)

    def move(self, pos):
        if self.windowState() == Qt.WindowMaximized or self.windowState() == Qt.WindowFullScreen:
            # 最大化或者全屏则不允许移动
            return
        super(FramelessWindow, self).move(pos)

    def showMaximized(self):
        """最大化,要去除上下左右边界,如果不去除则边框地方会有空隙"""
        super(FramelessWindow, self).showMaximized()
        self.layout().setContentsMargins(0, 0, 0, 0)

    def showNormal(self):
        """还原,要保留上下左右边界,否则没有边框无法调整"""
        super(FramelessWindow, self).showNormal()
        self.layout().setContentsMargins(
            self.Margins, self.Margins, self.Margins, self.Margins)

    def eventFilter(self, obj, event):
        """事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式"""
        if isinstance(event, QEnterEvent):
            self.setCursor(Qt.ArrowCursor)
        return super(FramelessWindow, self).eventFilter(obj, event)

    def paintEvent(self, event):
        """由于是全透明背景窗口,重绘事件中绘制透明度为1的难以发现的边框,用于调整窗口大小"""
        super(FramelessWindow, self).paintEvent(event)
        painter = QPainter(self)
        bar = self.barColor()
        height = self.barHeight()
        if not self.titleBar.isHidden():
            painter.setPen(self.barColor())
            painter.fillRect(QRect(0, 0, self.width(), self.barHeight()), bar)

            painter.setPen(QPen(self.border_color, 1))
            painter.drawRect(QRect(0, height, self.width() -
                                   1, self.height() - height - 1))

            painter.setPen(bar)
            painter.drawLine(0, height, self.width(), height)
        else:
            painter.setPen(self.border_color)
            painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        super(FramelessWindow, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self._mpos = event.pos()
            self._pressed = True

    def mouseReleaseEvent(self, event):
        '''鼠标弹起事件'''
        super(FramelessWindow, self).mouseReleaseEvent(event)
        self._pressed = False
        self.Direction = None

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super(FramelessWindow, self).mouseMoveEvent(event)
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
                self.Direction = LeftTop
                self.setCursor(Qt.SizeFDiagCursor)
            elif wm <= xPos <= self.width() and hm <= yPos <= self.height():
                # 右下角
                self.Direction = RightBottom
                self.setCursor(Qt.SizeFDiagCursor)
            elif wm <= xPos and yPos <= self.CurSorMargins:
                # 右上角
                self.Direction = RightTop
                self.setCursor(Qt.SizeBDiagCursor)
            elif xPos <= self.CurSorMargins and hm <= yPos:
                # 左下角
                self.Direction = LeftBottom
                self.setCursor(Qt.SizeBDiagCursor)
            elif 0 <= xPos <= self.CurSorMargins and self.CurSorMargins <= yPos <= hm:
                # 左边
                self.Direction = Left
                self.setCursor(Qt.SizeHorCursor)
            elif wm <= xPos <= self.width() and self.CurSorMargins <= yPos <= hm:
                # 右边
                self.Direction = Right
                self.setCursor(Qt.SizeHorCursor)
            elif self.CurSorMargins <= xPos <= wm and 0 <= yPos <= self.CurSorMargins:
                # 上面
                self.Direction = Top
                self.setCursor(Qt.SizeVerCursor)
            elif self.CurSorMargins <= xPos <= wm and hm <= yPos <= self.height():
                # 下面
                self.Direction = Bottom
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
        if self.Direction == LeftTop:  # 左上角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
        elif self.Direction == RightBottom:  # 右下角
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
        elif self.Direction == RightTop:  # 右上角
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos.setX(pos.x())
        elif self.Direction == LeftBottom:  # 左下角
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos.setY(pos.y())
        elif self.Direction == Left:  # 左边
            if w - xPos > self.minimumWidth():
                x += xPos
                w -= xPos
            else:
                return
        elif self.Direction == Right:  # 右边
            if w + xPos > self.minimumWidth():
                w += xPos
                self._mpos = pos
            else:
                return
        elif self.Direction == Top:  # 上面
            if h - yPos > self.minimumHeight():
                y += yPos
                h -= yPos
            else:
                return
        elif self.Direction == Bottom:  # 下面
            if h + yPos > self.minimumHeight():
                h += yPos
                self._mpos = pos
            else:
                return
        self.setGeometry(x, y, w, h)

    @property
    def window_size(self) -> QSize:
        return QApplication.desktop().size()

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.nestle_enable:
            self._hide_or_show('show', event)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if self.nestle_enable:
            self._hide_or_show('hide', event)

    def _hide_or_show(self, mode, event):
        pos = self.frameGeometry().topLeft()
        size = self.window_size
        pos = self.frameGeometry().topLeft()
        if mode == 'show' and self.moved:
            if pos.x() + self.width() >= size.width():  # 右侧显示
                self._start_animation(size.width() - self.width() + 2, pos.y())
                event.accept()
                self.moved = False
            elif pos.x() <= 0:  # 左侧显示
                self._start_animation(0, pos.y())
                event.accept()
                self.moved = False
            elif pos.y() <= 0:  # 顶层显示
                self._start_animation(pos.x(), 0)
                event.accept()
                self.moved = False
        elif mode == 'hide':
            if pos.x() + self.width() >= size.width():  # 右侧隐藏
                self._start_animation(size.width() - 2, pos.y())
                event.accept()
                self.moved = True
            elif pos.x() <= 2:  # 左侧隐藏
                self._start_animation(2 - self.width() + 1, pos.y())
                event.accept()
                self.moved = True
            elif pos.y() <= 2:  # 顶层隐藏
                self._start_animation(pos.x(), 2 - self.height())
                event.accept()
                self.moved = True

    def _start_animation(self, width, height):
        animation = QPropertyAnimation(self, b"geometry", self)
        startpos = self.geometry()
        animation.setDuration(200)
        newpos = QRect(width, height, startpos.width(), startpos.height())
        animation.setEndValue(newpos)
        animation.start()


class TitleWidget(FramelessWindow):

    @property
    def content_widget(self) -> QWidget:
        return self._widget

    c = content_widget

    def __init__(self, title: str, widget: QWidget = None, bar_color: Union[str, QColor] = '#426BDD',
                 parent: QWidget = None, auto_resize: bool = False, nestle_enable: bool = False, border_color=None):
        super().__init__(parent)
        self.border_color = border_color or self.border_color
        self.set_auto_resize(auto_resize)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setTitleBarColor(QColor(bar_color))
        self.setWindowTitle(title)
        self.nestle_enable = nestle_enable
        title_bar = self.titleBar
        title_bar.setTitleStyle('color: white')
        title_bar.buttonMaximum.hide()
        title_bar.buttonMinimum.setStyleSheet(
            'QPushButton{color:white}QPushButton:hover{background:rgb(109,139,222)}')
        title_bar.buttonClose.setStyleSheet(
            'QPushButton{color:white}QPushButton:hover{background: rgb(109,139,222)}')
        title_height = title_bar.titleLabel.fontMetrics().height() + 10
        self.setTitleBarHeight(title_height)
        if widget is not None:
            self.set_content_Widget(widget)

        self.setIconSize(16)
        self.setWindowIcon(QIcon(':/imgs/favicon.ico'))

    def hide_title_bar(self):
        self.titleBar.hide()

    def set_content_Widget(self, target: QWidget):
        target.root = self
        target.setWindowFlags(Qt.FramelessWindowHint)
        self.setWidget(target)
        self.override_widget()

    def setTextColor(self, color):
        self.titleBar.titleLabel.setStyleSheet(
            f'border:none;color: {QColor(color).name()}')

        s = '''
            QPushButton{color:  %s, border:none;background:transparent}
            QPushButton:hover{color: black;border:none}
        ''' % QColor(color).name()
        self.titleBar.buttonClose.setStyleSheet(s)
        self.titleBar.buttonMinimum.setStyleSheet(s)
        self.titleBar.buttonMaximum.setStyleSheet(s)

    def hide_titlebar_all(self):
        self.titleBar.buttonMinimum.hide()
        self.titleBar.buttonClose.hide()
        self.titleBar.buttonMaximum.hide()

    def hide_btns(self, close_btn=False, min_btn=False, max_btn=False):
        self.titleBar.buttonClose.setHidden(close_btn)
        self.titleBar.buttonMinimum.setHidden(min_btn)
        self.titleBar.buttonMaximum.setHidden(max_btn)

    def close_btn(self, style: str):
        f = QFont('Webdings')
        btn = QPushButton('r')
        btn.setFont(f)
        btn.clicked.connect(self.close)
        btn.setStyleSheet(style)
        return btn

    def min_btn(self, style):
        f = QFont('Webdings')
        btn = QPushButton('0')
        btn.setFont(f)
        btn.clicked.connect(self.showMinimized)
        btn.setStyleSheet(style)
        return btn

    def max_btn(self, style):
        f = QFont('Webdings')
        btn = QPushButton('1')
        btn.setFont(f)
        btn.clicked.connect(self.showMaximized)
        btn.setStyleSheet(style)
        return btn

    def override_widget(self):
        def move(this, point):
            if this.root:
                this.root.move(point)

        def show(this) -> None:
            if this.root:
                this.root.raise_()
                this.root.show()
                this.root.showNormal()

        def showNormal(this):
            if this.root:
                this.root.showNormal()

        def raise_(this) -> None:
            if this.root:
                this.root.raise_()

        def close(this):
            if this.root:
                this.root.close()
                if getattr(this, 'before_close', None) is not None:
                    try:
                        this.before_close()
                    except:
                        pass

        def exec_(this):
            if this.root:
                this.root.show()
                QDialog.exec_(self._widget)

        self._widget.move = MethodType(move, self._widget)
        self._widget.show = MethodType(show, self._widget)
        self._widget.raise_ = MethodType(raise_, self._widget)
        self._widget.close = MethodType(close, self._widget)
        self._widget.exec_ = MethodType(exec_, self._widget)
        self._widget.showNormal = MethodType(showNormal, self._widget)

    def closeEvent(self, a0) -> None:
        super().closeEvent(a0)
        self._widget.close()

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)


class PluginService(QObject):
    _instance = None
    _worker: BackgroundWorker = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__()
            cls._worker = BackgroundWorker()
        return cls._instance

    def add_coro(self, coro, call_back, err_back):
        self._worker.add_coro(coro, call_back=call_back, err_back=err_back)

    def add_task(self, func, args=(), kwargs={}, call_back=None, err_back=None):
        self._worker.add_task(func, args, kwargs, call_back, err_back)
