import uuid

import requests
from google.protobuf.empty_pb2 import Empty

from .core.interceptors import RestAuth


class RestExecutor:
    def __init__(self, client, base_url, root_certificates: str):
        self._client = client
        self._rest_auth = RestAuth(client)
        self._base_url = base_url
        self._root_certificates = root_certificates

    def post(self, url: str, body: str, params=None):
        response = requests.post(
            self._base_url + url,
            data=body,
            auth=self._rest_auth,
            params=params,
            verify=self._root_certificates if self._root_certificates else True,
            headers={
                "user-agent": f"feature-store-py-cli/{self._client._get_client_version()}",
                "content-type": "application/json",
                "request-id": str(uuid.uuid4()),
            },
        )

        response.raise_for_status()
        return response.json()

    def get(self, url: str, params=None):
        response = requests.get(
            self._base_url + url,
            auth=self._rest_auth,
            params=params,
            verify=self._root_certificates if self._root_certificates else True,
            headers={
                "user-agent": f"feature-store-py-cli/{self._client._get_client_version()}",
                "content-type": "application/json",
                "request-id": str(uuid.uuid4()),
            },
        )

        response.raise_for_status()
        return response.json()


class RestStub:
    def __init__(self, client, root_certificates: str):
        response = client._stub.GetApiConfig(Empty())
        self.online_store = RestExecutor(client, response.public_online_rest_api_url, root_certificates)
