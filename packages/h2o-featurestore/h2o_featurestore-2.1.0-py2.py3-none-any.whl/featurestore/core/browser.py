import logging
import webbrowser

from google.protobuf.empty_pb2 import Empty


class Browser:
    _instance = None
    _web_url = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)

        return cls._instance

    def __init__(self, stub):
        if self._web_url is None:
            response = stub.GetWebConfig(Empty())
            self._web_url = response.web_url

    def open_website(self, page=None):
        """This opens the Feature Store Web UI.

        This opens the returned URL in the browser (if it's not possible to open the browser, you will
        have to do this manually).

        For more details:
            https://docs.h2o.ai/featurestore/api/client_initialization
        """
        try:
            url = self._web_url + page if page else self._web_url
            webbrowser.get()
            webbrowser.open(url)
            logging.info(f"Opening browser to visit: {url}")
        except webbrowser.Error:
            logging.error(f"Browser is not supported. Please open " f"{url} manually.")
