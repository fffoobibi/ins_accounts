# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 15:54
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : editwidget.py
# @Software: PyCharm
from PyQt5.QtWidgets import QWidget
from ui.editui import Ui_Form


class EditWidget(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(3)
