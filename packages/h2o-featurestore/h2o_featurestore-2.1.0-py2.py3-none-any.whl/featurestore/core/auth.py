import asyncio
import datetime
import inspect
import logging
import re
import sys
import webbrowser

import grpc
from google.protobuf.empty_pb2 import Empty

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from featurestore.core.config import ConfigUtils

from .collections.pats import PersonalAccessTokens


class AuthWrapper:
    ACCESS_TOKEN_EXPIRES_SOON_SECS = 60

    def __init__(self, stub):
        self._stub = stub
        self._access_token = None
        self._access_token_expiration_date = None
        self._get_access_token_external = None
        self._props = ConfigUtils.collect_properties()
        self.pats = PersonalAccessTokens(self._stub)

    def get_active_user(self):
        """Obtain currently active user details.

        Returns:
            UserBasicInfo: Logged-in user details.

            For example:

            id: <user_id>
            name: <user_name>
            email: <user_email>
        """
        request = Empty()
        return self._stub.GetActiveUser(request).user

    def set_obtain_access_token_method(self, method):
        """Set a valid user access token.

        This will obtain an access token from the external environment to use for authentication.

        Args:
            method: (Callable) A method that returns a token from the external environment.

        For more details:
            https://docs.h2o.ai/featurestore/api/authentication.html#authentication-via-access-token-from-external-environment
        """
        self._get_access_token_external = method

    def logout(self):
        """Logout the current user session."""
        is_success, token_or_error = self._obtain_token()
        if is_success:
            if not AuthWrapper._is_personal_access_token(self._props["token"].data):
                request = pb.LogoutRequest()
                request.refresh_token = self._props["token"].data
                self._stub.Logout(request)
                self._access_token = None
                self._access_token_expiration_date = None
            ConfigUtils.delete_property(self._props, ConfigUtils.TOKEN_KEY)
            logging.info("You have been logged out.")
        else:
            logging.info("You are not logged in.")

    def login(self, open_browser=True):
        """User login via identity provider.

        This opens the returned URL in the browser (if it's not possible to open the browser, you will
        have to do this manually) and wait for the refresh token. Returned refresh tokens will be
        saved into the client’s configuration file.

        Args:
            open_browser: (bool) If True, opens the URL in the browser. Defaults to True.

        Raises:
            AuthException: Incorrect response or if user doesn't log in via browser,
              logging session will be expired.

        For more details:
            https://docs.h2o.ai/featurestore/api/authentication.html#authentication-via-refresh-token-from-identity-provider
        """
        try:
            sys.tracebacklimit = None
            for response in self._stub.Login(Empty()):
                if response.HasField("login_url"):
                    if open_browser:
                        try:
                            webbrowser.get()
                            webbrowser.open(response.login_url)
                            logging.info(f"Opening browser to visit: {response.login_url}")
                        except webbrowser.Error:
                            logging.error(
                                f"Browser is not supported: Please visit "
                                f"{response.login_url} to continue authentication."
                            )
                    else:
                        logging.info(f"Please visit {response.login_url} to continue authentication.")
                elif response.HasField("refresh_token"):
                    self.set_auth_token(response.refresh_token)
                else:
                    sys.tracebacklimit = 0
                    raise AuthException("Incorrect response")
        except grpc._channel._MultiThreadedRendezvous as error:
            logging.error("Your logging session expired, please login again by running client.auth.login().")
            logging.debug(f"Received RPC error during user login: code={error.code()} message={error.details()}")

    def set_auth_token(self, token):
        """Set user token for authentication.

        Args:
            token: (str) A personal access token.

        Raises:
            AuthException: If user is not authenticated or token is no longer valid.
        """
        sys.tracebacklimit = None
        ConfigUtils.store_token(self._props, token)
        if not AuthWrapper._is_personal_access_token(token):
            self._access_token = None
            self._access_token_expiration_date = None
            is_success, token_or_error = self._obtain_token()
            if not is_success:
                sys.tracebacklimit = 0
                raise AuthException(token_or_error)

    @staticmethod
    def _is_personal_access_token(token: str) -> bool:
        return re.match(r"^[a-z0-9]{3}_.*", token)

    def _is_access_token_expired(self):
        if not self._access_token:
            return True
        if self._access_token_expiration_date is not None:
            expires_in = (self._access_token_expiration_date - datetime.datetime.now()).total_seconds()
            return expires_in <= AuthWrapper.ACCESS_TOKEN_EXPIRES_SOON_SECS

        return False

    def _obtain_token(self):
        if self._get_access_token_external is not None:
            external_token = self._get_access_token_external()
            if inspect.isawaitable(external_token):
                loop = asyncio.get_event_loop()
                return True, loop.run_until_complete(external_token)
            else:
                return True, external_token
        elif ConfigUtils.TOKEN_KEY not in self._props:
            return (
                False,
                "You are not authenticated. Set personal access token or execute client.auth.login() method",
            )
        elif AuthWrapper._is_personal_access_token(ConfigUtils.get_token(self._props)):
            return True, ConfigUtils.get_token(self._props)
        elif self._is_access_token_expired():
            request = pb.RefreshTokenRequest()
            request.refresh_token = ConfigUtils.get_token(self._props)
            try:
                resp = self._stub.GetAccessToken(request)
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.UNAUTHENTICATED:
                    return (
                        False,
                        "The authentication token is no longer valid. Please login again.",
                    )
                else:
                    raise

            self._access_token = resp.access_token
            ConfigUtils.store_token(self._props, resp.refresh_token)
            self._access_token_expiration_date = datetime.datetime.now() + datetime.timedelta(seconds=resp.expires_in)
            return True, self._access_token
        else:
            return True, self._access_token

    def __repr__(self):
        return "This class wraps together methods related to Authentication"


class AuthException(Exception):
    pass
