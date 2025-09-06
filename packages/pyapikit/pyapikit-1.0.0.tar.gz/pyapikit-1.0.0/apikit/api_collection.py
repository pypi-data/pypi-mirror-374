# coding: utf-8

from typing import List
from .schema import API


class APICollection:
    def __init__(self, api_list: List[API]):
        self.api_list = api_list

    def get(self, name: str):
        for api in self.api_list:
            if api.name == name:
                return api
        return None

    def __getattribute__(self, name: str, /) -> API:
        # 对于 'get' 和其他内置属性，使用基类的 __getattribute__
        if name in ('get', 'api_list'):
            return super().__getattribute__(name)

        # 对于 API 名称，使用 get 方法
        api = self.get(name)
        if api is None:
            raise AttributeError(f"API {name} not found")
        return api

    def __getitem__(self, name: str) -> API:
        return self.get(name)

    def __iter__(self):
        return iter(self.apis)

    def __len__(self):
        return len(self.apis)

    def __contains__(self, name: str) -> bool:
        return self.get(name) is not None

    def __str__(self):
        return str(self.apis)

    def __repr__(self):
        return repr(self.apis)
