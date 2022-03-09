# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 15:54
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : editwidget.py
# @Software: PyCharm
from PyQt5.QtWidgets import QWidget, QMenu, QAction

from components.customwidgets import Images
from models import TableData
from ui.editui import Ui_Form


class EditWidget(QWidget, Ui_Form):
    def __init__(self, data: TableData):
        super().__init__()
        self.data = data
        self.setupUi(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(3)
        self.set_slots()
        # self.pushButton_8.setMenu()
        menu = QMenu()
        self.a1 = QAction('添加cookies')
        self.a2 = QAction('删除cookies')
        self.a3 = QAction('导出cookies')
        menu.addAction(self.a1)
        menu.addAction(self.a2)
        menu.addAction(self.a3)
        self.pushButton_8.setMenu(menu)


    def set_slots(self):
        self.pushButton_7.clicked.connect(self.show_image)

    def show_image(self):
        if self.data.fail_picture_path:
            if self.data.image_content:
                Images.display([self.data.image_content], '登录失败', )
