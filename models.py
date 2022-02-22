# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 15:40
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : models.py
# @Software: PyCharm
from typing import List

from pydantic import BaseModel, validator, Field


class TableData(BaseModel):
    index: str = None
    account_name: str = Field(None, alias='user')
    passwd: str = Field(None, alias='passwd')
    ip: str
    can_use: str = Field(None, alias='can_login')
    schedule: str = Field(None)

    @validator('can_use', always=True, pre=True)
    def _check_can_use(cls, v):
        if v == 0:
            return '不能登录'
        elif v == 1:
            return '可以登录'
        elif v == -1:
            return '未检测'
        else:
            return '未知'

    @validator('schedule', always=True, pre=True)
    def _check_schedule(cls, v):
        if v == 0:
            return '不调度'
        elif v == 1:
            return '调度检测'
        else:
            return '未知'

    @classmethod
    def from_iter(cls, values) -> List['TableData']:
        return [cls.parse_obj(d) for d in values]


class RunTimeData(BaseModel):
    token: str

    # @validator('can_use', always=True, pre=True)
    # def _check_can_use(cls, v, field):
    #     if isinstance(v, bool):
    #         return '可用' if v else '不可用'
    #     return v
