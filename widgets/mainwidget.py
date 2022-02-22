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

from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QHeaderView, QTableWidgetItem, QVBoxLayout, \
    QPushButton, QTextEdit
from PyQt5.QtCore import Qt, QSettings, pyqtProperty

from components.styles import Sh
from widgets.editwidget import EditWidget
from ui.mainui import Ui_Form
from models import TableData
from constants import DEBUG
from components.customwidgets import BackgroundWorker, Message, Loading, Modal, TitleWidget
from sources_rc import *

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


class Main(QWidget, Ui_Form):
    from request import get, post

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._title = TitleWidget('ins账号管理', self, bar_color='#1B1C24', auto_resize=True, border_color=Qt.transparent)
        self.setupUi(self)
        self.init()
        self.set_slots()
        if DEBUG:
            self.test()

    def init(self):
        def update_table_style(item: QTableWidgetItem):
            index = table.indexFromItem(item)
            row = index.row()
            table.selectRow(row)

        self._title.setStyleSheet('TitleWidget{background:#414450 }')
        self.setStyleSheet('Main{background: #414450}QLabel{color: white}'
                           'QLabel{font-family: 微软雅黑;color:white}'
                           'QLineEdit{background: #3A3D4C;font-family: 微软雅黑;color:white;border:1px solid #282A36;padding:2px 2px;}'
                           'QPushButton{background-color:#6272A4;border: 1px solid #282A36; padding:0px 5px;'
                           'border-radius:3px;color:lightgray; font-family: 微软雅黑;height:20px}')
        self.setWindowTitle('Ins账号管理')
        table = self.tableWidget
        table.itemClicked.connect(update_table_style)
        table.setShowGrid(False)
        table.setColumnWidth(0, 40)
        table.setStyleSheet('''
            QTableWidget{outline: 0px;background:#282A36}
            QTableWidget::item{border:none;border-bottom:1px solid gray;color:black;background-color:#282A36;color:white}
            QTableWidget::item:selected{background-color:#666B87}
            QTableWidget::item:hover{background-color:#44475A}
        ''')
        table.verticalScrollBar().setStyleSheet(Sh.table_v_scroll_style)
        table.horizontalScrollBar().setStyleSheet(Sh.table_h_scroll_style)

        horizon = self.tableWidget.horizontalHeader()
        horizon.setStyleSheet(Sh.header_view_style)
        horizon.setSectionResizeMode(QHeaderView.Stretch)
        horizon.setSectionResizeMode(0, QHeaderView.Fixed)
        horizon.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        horizon.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        horizon.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        horizon.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        # horizon.setSectionResizeMode(5, QHeaderView.ResizeToContents)

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
            Message.info(f'{ret}', self)
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

    def delete_account(self):
        pass

    def modify_account(self):
        pass

    def add_account_cookies(self):
        def add():
            self.worker.add_coro(_post(), call_back, err_back)

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
            pass

        def err_back(error):
            pass

        content = QWidget()
        lay = QVBoxLayout(content)
        content.text_edit = QTextEdit()
        lay.addWidget(content.text_edit)
        lay.addWidget(QPushButton('确认', clicked=add))
        Modal.show('添加cookies', content, self)

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
        count = self.tableWidget.rowCount()
        table = self.tableWidget
        texts = [data.index, data.account_name, data.passwd, data.ip, data.can_use]
        table.setRowCount(count + 1)
        table.setRowHeight(count + 1, 100)
        for index, text in enumerate(texts):
            item = TableWidgetItem()
            item.setText(text)
            item.setToolTip(text)
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(count, index, item)

        widget = EditWidget()
        table.setCellWidget(count, 5, widget)
        widget.pushButton.clicked.connect(self.add_account_cookies)

    @classmethod
    def run(cls):
        app = QApplication(sys.argv)
        self = cls()
        self.show()
        sys.exit(app.exec_())
