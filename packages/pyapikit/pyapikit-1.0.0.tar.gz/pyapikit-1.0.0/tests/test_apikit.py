from dataclasses import dataclass
import unittest
import requests
from apikit.schema import API, BaseRequest, BaseResponse
from apikit.api_collection import APICollection
from apikit.client import Client
from apikit.envvar import EnvVar


@dataclass
class CharacterRequest(BaseRequest):
    pass


@dataclass
class CharacterResponse(BaseResponse):
    character_name: str = ''
    xmov_id: str = ''

    @staticmethod
    def from_response(response: requests.Response):
        d = response.json()
        return CharacterResponse(
            character_name=d.get("character_name", "mock_character_name"),
            xmov_id=d.get("xmov_id", "mock_xmov_id")
        )


class TestAPICollection(unittest.TestCase):
    def setUp(self):
        self.api_collection = APICollection(api_list=[API(name="get_character_list",
                                                          method="GET",
                                                          url="/a",
                                                          description="这是一段描述",
                                                          request_schema=CharacterRequest,
                                                          response_schema=CharacterResponse
                                                          ),
                                                      API(name="b",
                                                          method="POST",
                                                          url="/b",
                                                          description="b description"
                                                          )
                                                      ]
                                            )

        self.client = Client(endpoint="http://localhost:8000",
                             api_collection=self.api_collection)

    def test_api_collection(self):

        print("api_collection.get_character_list: ", self.api_collection.get_character_list)
        print("api_collection.get_character_list.method: ", self.api_collection.get_character_list.method)
        print("api_collection.get_character_list.url: ", self.api_collection.get_character_list.url)
        print("api_collection.a.description: ",
              self.api_collection.get_character_list.description)
        print("api_collection.get_character_list.login_required: ",
              self.api_collection.get_character_list.login_required)
        self.assertEqual(self.api_collection.get_character_list.method, "GET")
        self.assertEqual(self.api_collection.b.method, "POST")
        self.assertEqual(self.api_collection.get_character_list.url, "/a")
        self.assertEqual(self.api_collection.b.url, "/b")
        self.assertEqual(self.api_collection.get_character_list.login_required, True)
        self.assertEqual(self.api_collection.b.login_required, True)

    def test_client(self):
        print("client.endpoint: ", self.client.endpoint)
        get_character_list: API = self.client.get_character_list
        print("api: ", get_character_list)
        self.assertEqual(get_character_list.method, "GET")
        self.assertEqual(get_character_list.url, "/a")
        self.assertEqual(get_character_list.login_required, True)
        self.assertEqual(get_character_list.description, "这是一段描述")

        response: CharacterResponse = self.client._request(
            get_character_list, CharacterRequest(params={}, data={}, headers={}), is_mock=True)
        print("response: ", response)
        self.assertEqual(response.error_code, 0)
        self.assertEqual(response.error_reason, "")
