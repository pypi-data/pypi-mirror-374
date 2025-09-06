import unittest
from apikit import Client, API, APICollection, BaseRequest, BaseResponse

class CharacterRequest(BaseRequest):
    character_name:str = ''
    xmov_id:str = ''

class CharacterResponse(BaseResponse):
    character_name:str = ''
    xmov_id:str = ''


class TestTTSALite(unittest.TestCase):
    def setUp(self):
        self.client = Client(endpoint="http://localhost:8000",
        api_collection=APICollection(
            api_list=[
                API(
                    name="open",
                    method="POST",
                    url="/session",
                    description="open session",
                    request_schema=BaseRequest,
                    response_schema=BaseResponse
                ),
                API(
                    name="close",
                    method="DELETE",
                    url="/session",
                    description="close session",
                    request_schema=BaseRequest,
                    response_schema=BaseResponse
                )
            ]
        ))
    def test_ttsa_lite(self):
        response = self.client.open(BaseRequest())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"character_name": "mock_character_name", "xmov_id": "mock_xmov_id"})
        response = self.client.close()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"character_name": "mock_character_name", "xmov_id": "mock_xmov_id"})

    def test_callable(self):
        class Dog(object):
            def __init__(self, name):
                self.name = name
            def __call__(self, client:Client, **kwargs):
                print(client)
                return "woof"
        dog = Dog("Rex")
        self.assertEqual(dog(client=self.client), "woof")

if __name__ == "__main__":
    unittest.main()