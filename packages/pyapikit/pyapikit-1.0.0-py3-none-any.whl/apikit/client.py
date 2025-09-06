# coding: utf-8
import requests

from .api_collection import APICollection
from .schema import API, BaseRequest, BaseResponse, APIRequestProtocol, APIResponseProtocol, APIClientProtocol

class Client(APIClientProtocol):
    def __init__(self, endpoint: str, api_collection: APICollection, is_mock: bool = True):
        self.endpoint = endpoint
        self.api_collection = api_collection
        self.is_mock = is_mock

    # def get(self, request: BaseRequest):
    #     return self.request(request)

    # def post(self, request: BaseRequest):
    #     return self.request(request)

    def _request(self, api: API, request: BaseRequest, is_mock: bool = False) -> APIResponseProtocol:
        url = self.endpoint + api.url
        if self.is_mock or is_mock:
            print("mock request: ", request)
            return api.response_schema(character_name="mock_response_data", xmov_id="mock_response_data")
        response = requests.request(api.method, url, data=request.data, params=request.params, headers=request.headers) 
        return api.response_schema.from_response(response)
    
    def __getattr__(self, name: str, /) -> API:
        api = self.api_collection.get(name)
        if api is None:
            raise AttributeError(f"API {name} not found")
        return api
    
    def __getitem__(self, name: str) -> API:
        return self.api_collection.get(name)
    
    