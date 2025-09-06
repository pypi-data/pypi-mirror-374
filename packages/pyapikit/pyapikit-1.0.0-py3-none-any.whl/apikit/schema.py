# coding: utf-8

from dataclasses import dataclass, asdict
from typing import Any, Optional, Protocol
import requests


class APIClientProtocol(Protocol):
    def _request(self, api: 'API', request: 'APIRequestProtocol', is_mock: bool = False) -> 'APIResponseProtocol':
        pass


class APIRequestProtocol(Protocol):
    def is_request(self):
        return True


class APIResponseProtocol(Protocol):
    def from_response(self, response: requests.Response):
        return self


@dataclass
class BaseRequest:
    params: Optional[dict] = None
    data: Optional[dict] = None
    headers: Optional[dict] = None

    def to_dict(self):
        return asdict(self)

    def is_request(self):
        return True

    def __add__(self, other: 'BaseRequest'):
        params = self.params.copy() if self.params else {}
        data = self.data.copy() if self.data else {}
        headers = self.headers.copy() if self.headers else {}

        other_params = other.params or {}
        other_data = other.data or {}
        other_headers = other.headers or {}

        params.update(other_params)
        data.update(other_data)
        headers.update(other_headers)

        return BaseRequest(
            params=params,
            data=data,
            headers=headers
        )


@dataclass
class BaseResponse:
    error_code: int = 0
    error_reason: str = ""
    data: Optional[dict] = None
    raw_data: Optional[dict] = None

    @staticmethod
    def from_response(response: requests.Response):
        """从响应数据中创建一个 BaseResponse 对象。

        Args:
            response (requests.Response): 响应数据对象

        Returns:
            BaseResponse: 创建的 BaseResponse 对象
        """
        d = response.json()
        return BaseResponse(
            error_code=d.get("error_code", 0),
            error_reason=d.get("error_reason", ""),
            data=d.get("data", {}),
            raw_data=d
        )

    def is_response(self):
        return True

    def to_dict(self):
        return asdict(self)


@dataclass
class API:
    """表示一个 API 接口的类。
    
    这个类用于定义一个 API 接口的所有必要信息，包括名称、HTTP 方法、URL、描述等。
    它还包含了请求和响应的数据模式定义。
    """
    
    #: API 接口的名称
    name: str
    
    #: HTTP 请求方法 (GET, POST, PUT, DELETE 等)
    method: str
    
    #: API 接口的 URL 地址
    url: str
    
    #: API 接口的描述信息
    description: str = ""
    
    #: 是否需要登录认证
    login_required: bool = True
    
    #: 请求数据的模式类
    request_schema: APIRequestProtocol = BaseRequest
    
    #: 响应数据的模式类
    response_schema: APIResponseProtocol = BaseResponse

    def __call__(self, client: APIClientProtocol, request: APIRequestProtocol, is_mock: bool = False) -> APIResponseProtocol:
        """执行 API 请求。

        Args:
            client (APIClientProtocol): API 客户端实例
            request (APIRequestProtocol): 请求数据对象
            is_mock (bool, optional): 是否使用模拟数据，默认为 False

        Returns:
            APIResponseProtocol: API 响应数据对象
        """
        return client._request(self, request, is_mock)
