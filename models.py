# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 15:40
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : models.py
# @Software: PyCharm
from typing import List

import aiohttp
from pydantic import BaseModel, validator, Field


class TableData(BaseModel):
    index: str = None
    account_name: str = Field(None, alias='user')
    passwd: str = Field(None, alias='passwd')
    ip: str
    can_use: str = Field(None, alias='can_login')
    schedule: str = Field(None)
    fail_picture_path: str = None
    image_content: bytes = None

    @validator('fail_picture_path', always=True, pre=True)
    def _check_fail_picture(cls, v, values):
        user = values.get('account_name')
        can_use = values.get('can_use')
        if can_use == '不能登录':
            return f'/static/fails/{user}.png'

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

    def fetch_image(self, url, worker, call_back=None, err_back=None):
        async def _fetch():
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as sess:
                async with sess.get(url) as resp:
                    content = await resp.content.read()
                    self.image_content = content

        worker.add_coro(_fetch(), call_back, err_back)


class RunTimeData(BaseModel):
    token: str

    # @validator('can_use', always=True, pre=True)
    # def _check_can_use(cls, v, field):
    #     if isinstance(v, bool):
    #         return '可用' if v else '不可用'
    #     return v
