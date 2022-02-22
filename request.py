# -*- coding: utf-8 -*-
# @Time    : 2022/2/21 15:41
# @Author  : fatebibi
# @Email   : 2836204894@qq.com
# @File    : request.py
# @Software: PyCharm

from constants import TIME_OUT, DEBUG

from typing import Union, List
from typing_extensions import Literal
from aiohttp import ClientSession, ClientTimeout, FormData


async def post(self, url: str, data: Union[dict, FormData] = None, session: ClientSession = None,
               timeout=TIME_OUT, ret: Literal['json', 'text'] = 'json', json=None):
    timeout = ClientTimeout(total=timeout)
    if session:
        async with session.post(url, data=data, timeout=timeout, json=json) as resp:
            if DEBUG:
                print(await resp.text())
            call = resp.json() if ret == 'json' else resp.text()
            return await call
    else:
        async with ClientSession() as sess:
            async with sess.post(url, data=data, timeout=timeout, json=json) as resp:
                call = resp.json() if ret == 'json' else resp.text()
                return await call


async def get(self, url: str, params: dict = None, session: ClientSession = None,
              timeout=TIME_OUT, ret: Literal['json', 'text'] = 'json'):
    timeout = ClientTimeout(total=timeout)
    if session:
        async with session.get(url, params=params, timeout=timeout) as resp:
            call = resp.json() if ret == 'json' else resp.text()
            return await call
    else:
        async with ClientSession() as sess:
            async with sess.get(url, params=params, timeout=timeout) as resp:
                call = resp.json() if ret == 'json' else resp.text()
                return await call
