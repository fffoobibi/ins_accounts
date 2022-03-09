# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 15:32
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : mainwidget.py
# @Software: PyCharm
import sys

import ujson
import aiohttp

from typing import List
from pathlib import Path

from PyQt5.QtGui import QColor, QPainter, QPalette, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QHeaderView, QTableWidgetItem, QVBoxLayout, \
    QPushButton, QTextEdit, QListWidget, QItemDelegate, QStyledItemDelegate, QStyle, QLabel, QFrame, QHBoxLayout, \
    QLineEdit, QGridLayout, QCheckBox, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QSettings, pyqtProperty, QModelIndex

from components.styles import Sh
from widgets.editwidget import EditWidget
from ui.mainui import Ui_Form
from models import TableData
from constants import DEBUG
from components.customwidgets import BackgroundWorker, Message, Loading, Modal, TitleWidget, color
from sources_rc import *

TitleWidget.config(
    text_color=Qt.lightGray,
    bar_color=QColor('#282A36'), #3A3D4C 282A36
    border_color=QColor('#282A36'),
    button_hide_policy={'max'}
)

fake_table = [{'index': 0, 'account_name': 'tests', 'passwd': 'sdfs', 'ip': '123.12.12', 'can_use': False}] * 5


class TableWidgetItem(QTableWidgetItem):
    def __init__(self):
        super(TableWidgetItem, self).__init__()
        self._type = '1'  # 1 normal; 2 selected; 3 hover;

    @pyqtProperty(str)
    def type(self):
        return self._type

    @type.setter
    def type(self, value: int):
        self._type = value


class Delegrate(QStyledItemDelegate):
    def __init__(self, hover, normal, selected):
        super(Delegrate, self).__init__()
        self.hover = hover
        self.normal = normal
        self.selected = selected

    def paint(self, painter: QPainter, option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
        value = index.data(Qt.DisplayRole)
        # p = painter

        if option.state == QStyle.State_Selected:
            bkg_color = self.selected
        elif option.state == QStyle.State_HasFocus:
            bkg_color = self.hover
        else:
            bkg_color = self.normal
        painter.fillRect(option.rect, bkg_color)

        # background_color = option.palette.color(QPalette.Background)
        if value == '不能登录':
            painter.setPen(Qt.red)
        elif value == '可以登录':
            painter.setPen(Qt.green)
        else:
            painter.setPen(Qt.white)
        painter.drawText(option.rect, Qt.AlignCenter, value)

        painter.setPen(Qt.gray)
        painter.drawLine(option.rect.bottomLeft(), option.rect.bottomRight())

        # QApplication.style().drawItemText(painter, option.rect, Qt.AlignCenter, option.palette, True, value, QPalette.Text )
        # super(Delegrate, self).paint(p, option, index)
        # p.drawText(option.rect, Qt.AlignCenter, value)


class Main(QWidget, Ui_Form):
    from request import get, post

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.root = TitleWidget('ins账号管理', self, auto_resize=True, nestle_enable=True)
        self.setupUi(self)
        self.init()
        self.set_slots()
        if DEBUG:
            self.test()

    def set_style_sheet(self):
        self.root.setStyleSheet('TitleWidget{background:#414450 }')
        self.setStyleSheet('Main{background: #414450}QLabel{color: white}'
                           'QLabel{font-family: 微软雅黑;color:white}'
                           'QLineEdit{background: #3A3D4C;font-family: 微软雅黑;color:white;border:1px solid #282A36;padding:2px 2px;}'
                           'QPushButton{background-color:#282A36;border: 1px solid #282A36; padding:2px 8px;'
                           'border-radius:3px;color:lightgray; font-family: 微软雅黑;height:20px}'
                           'QPushButton:hover{background-color: #414450}')

        self.tableWidget.setStyleSheet('''
            QTableWidget{outline: 0px;background:#282A36;border:1px solid #282A36}
            QTableWidget::item{border:none;border-bottom:1px solid gray;color:black;background-color:#282A36;color:white}
            QTableWidget::item:selected{background-color:#666B87}
            QTableWidget::item:hover{background-color:#44475A}
        ''')
        self.tableWidget.verticalScrollBar().setStyleSheet(Sh.table_v_scroll_style)
        self.tableWidget.horizontalScrollBar().setStyleSheet(Sh.table_h_scroll_style)

    def init(self):
        def update_table_style(item: QTableWidgetItem):
            index = table.indexFromItem(item)
            row = index.row()
            table.selectRow(row)

        self.set_style_sheet()
        self.setWindowTitle('Ins账号管理')
        table = self.tableWidget
        table.setMouseTracking(True)
        # table.setItemDelegateForColumn(4, Delegrate(QColor('#44475A'), QColor('#282A36'), QColor('#666B87')))
        # table.itemClicked.connect(update_table_style)
        # table.itemEntered.connect(update_table_style)
        table.setShowGrid(False)
        table.setColumnWidth(0, 40)

        table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        table.verticalScrollBar().setSingleStep(5)
        table.horizontalScrollBar().setSingleStep(5)

        horizon = self.tableWidget.horizontalHeader()
        horizon.setStyleSheet(Sh.header_view_style)
        horizon.setSectionResizeMode(QHeaderView.Stretch)
        horizon.setSectionResizeMode(0, QHeaderView.Fixed)
        horizon.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        horizon.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        horizon.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        horizon.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        horizon.setSectionResizeMode(5, QHeaderView.ResizeToContents | QHeaderView.Stretch)

        vertical = self.tableWidget.verticalHeader()
        vertical.hide()

        self.frame_2.layout().setContentsMargins(0, 0, 0, 0)
        self.worker = BackgroundWorker()
        self.settings = self._create_settings_file()

        self.load_from_settings()
        self.login()

    def set_slots(self):
        def fetch():
            self.settings.setValue('basic/domain', self.lineEdit.text().strip())
            self.get_accounts()

        self.pushButton_4.clicked.connect(fetch)
        self.pushButton_2.clicked.connect(self.add_accounts)  # 添加账号

    def _create_settings_file(self):
        settings = QSettings(str(Path.home()), QSettings.IniFormat)
        settings.setIniCodec("UTF-8")
        return settings

    def load_from_settings(self):
        self.lineEdit.setText(self.settings.value('basic/domain', 'http://35.174.29.43:4000'))

    # test
    def test(self):
        datas = [TableData.parse_obj(d) for d in fake_table]
        self.add_edit_items(datas)

    # api
    def api(self, path: str) -> str:
        return f'{self.lineEdit.text().strip()}{path}'

    def get_token(self):
        return self._token

    def login(self):
        self.lineEdit_2.setText('root')
        self.lineEdit_3.setText('qwer123456')
        data = {'username': 'root', 'password': 'qwer123456'}
        url = self.api('/login')

        if DEBUG:
            print('url: ', url)

        async def _login():
            async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
                js = await self.post(url, json=data, session=session)
                return js

        def call_back(ret):
            # Message.info(f'{ret}', self)
            self._token = ret.get('token')

        def err_back(error):
            Message.warn(f'{error}', self)

        self.worker.add_coro(_login(), call_back, err_back)

    def get_accounts(self):
        url = self.api('/ins/insList')

        async def _get():
            async with aiohttp.ClientSession() as session:
                js = await self.get(url, session=session)
                return TableData.from_iter(js)

        def call_back(ret):
            Loading.end(self.tableWidget)
            self.add_edit_items(ret)

        def err_back(error):
            Loading.end(self.tableWidget)
            Message.warn(f'{error}', self)

        Loading.load(self.tableWidget)
        self.worker.add_coro(_get(), call_back, err_back)

    def add_account(self):
        async def _post():
            url = self.api('/ins/addAccounts')
            data = {'token': self.get_token()}
            async with aiohttp.ClientSession() as session:
                js = await self.post(url, data=data, session=session)
                return js

        def call_back(ret):
            Message.info(f'{ret}', self)

        def err_back(error):
            Message.warn(f'{error}', self)

        self.worker.add_coro(_post(), call_back, err_back)

    def add_accounts(self):
        async def post():
            url = self.api('/ins/addAccounts')
            data = {'acc_list': text_edit.toPlainText(), 'token': self.get_token()}
            async with aiohttp.ClientSession(json_serialize=ujson.dumps,
                                             timeout=aiohttp.ClientTimeout(total=60)) as sess:
                js_data = await self.post(url, json=data, session=sess)
                if js_data.get('state') == 1:
                    return js_data.get('extra')
                raise Exception(js_data.get('extra'))

        def call_back(ret):
            Message.info(f'{ret}', self)

        def err_back(error):
            Message.warn(f'{error}', self)
            content.close()

        def sync_post():
            text = text_edit.toPlainText()
            ret = []
            for line in text:
                try:
                    user, passwd, ip = line.strip().split(';;')
                    ret.append(dict(user=user.strip(), passwd=passwd.strip(), ip=ip.strip()))
                except:
                    ret.append(False)
            if all(ret):
                Loading.load(content)
                self.worker.add_coro(post(), call_back, err_back)
            else:
                Message.warn(f'请按照正确的格式输入内容', self)

        content = QWidget()
        lay = QGridLayout(content)
        text_edit = QTextEdit()
        text_edit.setPlaceholderText('账户名,密码,ip, 用;;分隔')
        text_edit.setFont(QFont('微软雅黑'))
        text_edit.setContextMenuPolicy(Qt.NoContextMenu)
        lay.addWidget(text_edit, 0, 0, 2, 2)

        content.resize(300, 200)
        Modal.show('添加账号', content, self, center=False, call_back=sync_post, cancel_back=lambda: 1)

    def delete_account(self):
        pass

    def modify_account(self, data: TableData):
        def post():
            self.worker.add_coro(modify(), call_back, err_back)

        async def modify():
            url = self.api('/ins/editAccount')
            post_data = {'acc': data.account_name,
                         'ip': line1.text(),
                         'passwd': line2.text(),
                         'schedule': 1 if checkbox.isChecked() else 0}
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60),
                                             json_serialize=ujson.dumps) as sess:
                js_data = await self.post(url, session=sess, json=post_data)
                return js_data

        def call_back(ret):
            Message.info(f'{ret}', self)
            content.close()

        def err_back(error):
            Message.warn(f'{error}', self)

        content = QWidget()

        line1 = QLineEdit()
        line2 = QLineEdit()
        line1.setClearButtonEnabled(True)
        line2.setClearButtonEnabled(True)
        line1.setContextMenuPolicy(Qt.NoContextMenu)
        line2.setContextMenuPolicy(Qt.NoContextMenu)
        line1.setText(data.passwd)
        line2.setText(data.ip)

        checkbox = QCheckBox('')
        if data.schedule == '调度检测':
            checkbox.setChecked(True)
        else:
            checkbox.setChecked(False)

        lay = QGridLayout(content)
        lay.addWidget(QLabel('密码'), 0, 0)
        lay.addWidget(line1, 0, 1)
        lay.addWidget(QLabel('ip'), 1, 0)
        lay.addWidget(line2, 1, 1)
        lay.addWidget(QLabel('调度'), 2, 0)
        lay.addWidget(checkbox, 2, 1)

        content.setStyleSheet('QLabel{color: white; background: transparent}QWidget{background: transparent}')
        content.resize(300, 200)

        Modal.show('编辑', content, self, center=False,
                   call_back=post,
                   cancel_back=lambda: content.close())

    def check_account(self, account: dict):
        async def post():
            url = self.api('/ins/checkAccount')
            data = {'account': account, 'token': self.get_token()}
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60),
                                             json_serialize=ujson.dumps) as sess:
                js_data = await self.post(url, json=data, session=sess)
                if js_data.get('can_login'):
                    return '账号可以登录'
                else:
                    raise Exception('账号不可以登录!')

        def call_back(ret):
            Loading.end(self)
            Message.info(f'{ret}', self)

        def err_back(error):
            Loading.end(self)
            Message.warn(f'{error}', self)

        Loading.load(self)
        self.worker.add_coro(post(), call_back, err_back)

    def get_account_cookies(self, account_name):
        async def _fetch():
            url = self.api('/ins/getCookies')
            data = {'acc': account_name, 'token': self.get_token()}
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60),
                                             json_serialize=ujson.dumps) as session:
                js_data = await self.post(url, json=data, session=session)
                if js_data.get('status') == 1:
                    return js_data.get('value')
                elif js_data.get('status') == 0:
                    raise Exception('暂无cookies')

        def call_back(ret):
            Loading.end(self)
            QApplication.clipboard().setText(str(ret))
            Message.info(f'cookies 已复制', self)

        def err_back(error):
            Loading.end(self)
            Message.warn(f'{error}', self)

        Loading.load(self)
        self.worker.add_coro(_fetch(), call_back, err_back)

    def add_account_cookies(self):
        def add():
            if content.text_edit.toPlainText().strip():
                Loading.load(self)
                self.worker.add_coro(_post(), call_back, err_back)
            else:
                Message.warn(f'请输入cookies', content, duration=3000)
                return False

        async def _post():
            url = self.api('/ins/getAccount')
            data = {
                'acc': 'root',
                'acc_cookies': '',
                'token': self.get_token()
            }
            async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
                js = await self.post(url, json=data, session=session)
                return js

        def call_back(ret):
            Loading.end(self)

        def err_back(error):
            Loading.end(self)
            Message.warn(f'{error}', self)

        content = QWidget()
        lay = QVBoxLayout(content)
        content.text_edit = QTextEdit()
        lay.addWidget(content.text_edit)
        # lay.addWidget(QPushButton('确认', clicked=add))
        Modal.show('添加cookies', content, self, call_back=add)

    def delete_account_cookies(self):
        pass

    # 操作
    def add_edit_items(self, datas: List[TableData]):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        for index, data in enumerate(datas, 1):
            data.index = str(index)
            self.add_edit_item(data)

    def add_edit_item(self, data: TableData):
        def click(this, event):
            this.__class__.mouseMoveEvent(this, event)
            self.tableWidget.selectRow(count)

        count = self.tableWidget.rowCount()
        table = self.tableWidget
        texts = [data.index, data.account_name, data.passwd, data.ip]  # data.can_use
        table.setRowCount(count + 1)
        table.setRowHeight(count + 1, 100)
        for index, text in enumerate(texts):
            item = QTableWidgetItem()
            item.setText(text)
            item.setToolTip(text)
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(count, index, item)

        label = QLabel()
        label.setText(data.can_use)
        label.setAttribute(Qt.WA_TransparentForMouseEvents)
        label.setAlignment(Qt.AlignCenter)
        if data.can_use == '可以登录':
            color = 'green'
        elif data.can_use == '不能登录':
            color = 'red'
        else:
            color = 'white'
        label.setStyleSheet(f'color: {color};background-color: transparent')
        table.setCellWidget(count, 4, label)

        widget = EditWidget(data)
        widget.setMouseTracking(True)
        table.setCellWidget(count, 5, widget)

        widget.pushButton.hide()
        widget.pushButton_2.hide()  # 删除
        widget.pushButton_3.hide()
        widget.pushButton_4.hide()

        widget.pushButton_6.clicked.connect(lambda: self.check_account({'user': data.account_name, 'ip': data.ip}))

        widget.a1.triggered.connect(self.add_account_cookies)  # 添加cookies
        widget.a2.triggered.connect(lambda: self.get_token(data.account_name))  # 删除cookies
        widget.a3.triggered.connect(lambda: self.get_account_cookies(data.account_name))  # 导出cookies

        if data.fail_picture_path:
            data.fetch_image(self.api(data.fail_picture_path), self.worker)

    @classmethod
    def run(cls):
        app = QApplication(sys.argv)
        self = cls()
        self.show()
        sys.exit(app.exec_())
