import datetime
from typing import List

from dateutil.tz import gettz
from google.protobuf.duration_pb2 import Duration
from google.protobuf.empty_pb2 import Empty
from google.protobuf.timestamp_pb2 import Timestamp

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from .. import interactive_console
from ..entities.pat import PersonalAccessToken
from ..utils import Utils


class PersonalAccessTokens:
    def __init__(self, stub):
        self._stub = stub

    def generate(self, name: str, description: str, expiry_date: str = None, timezone: str = None) -> str:
        """Generate a personal access token for the currently logged-in user.

        Args:
            name: (str) A token name.
            description: (str) A description about the token.
            expiry_date: (str) Object represents a date string with format dd/MM/yyyy. Default is None.
            timezone: (str) Object represents a time zone name (Eg: 'America/Chicago'). Default is None.

        Returns:
            str: A token string for authentication.

        Typical example:
            token_str = client.auth.pats.generate(name="background_jobs", description="some description",
              expiry_date="<dd/MM/yyyy>", timezone=None)

        Raises:
            Exception: Invalid timezone.
            ValueError: Expiry date must be in the format: dd/MM/yyyy.

        For more details:
            https://docs.h2o.ai/featurestore/api/authentication.html#authentication-via-personal-access-tokens-pats
        """
        request = pb.GenerateTokenRequest()
        request.name = name
        request.description = description
        if expiry_date:
            try:
                if timezone:
                    desired_timezone = gettz(timezone)
                    if not desired_timezone:
                        raise Exception("Invalid timezone id: '{}'".format(timezone))
                else:
                    desired_timezone = None
                expiration = datetime.datetime.strptime(expiry_date, "%d/%m/%Y").astimezone(desired_timezone)
                timestamp = Timestamp()
                timestamp.FromDatetime(expiration)
                request.expiry_date.CopyFrom(timestamp)
            except ValueError:
                raise Exception("Expiry date must be in the format: dd/MM/yyyy")
        response = self._stub.GenerateToken(request)

        if not expiry_date:
            expire_date_used = Utils.timestamp_to_string(response.token_expiry_date)
            interactive_console.log("As expiry_date wasn't explicitly specified,")
            interactive_console.log(f"it was set to {expire_date_used} according to feature store policies.")
            interactive_console.log("Call client.auth.pats.maximum_allowed_token_duration to find out a limit.")

        return response.token

    def list(self, query: str = None) -> List[PersonalAccessToken]:
        """Return a generator which obtains the personal access tokens owned by current user, lazily.

        Args:
            query: (str) the name or description by which to search for the personal access tokens

        Returns:
            Iterable[PersonalAccessToken]: A generator iterator object consists of personal access tokens.

        Typical example:
            client.auth.pats.list()
        """
        request = pb.ListPersonalAccessTokensRequest()
        if query:
            request.query = query

        while request:
            response = self._stub.ListPersonalAccessTokens(request)
            if response.next_page_token:
                request.page_token = response.next_page_token
            else:
                request = None
            for pat in response.personal_access_tokens:
                yield PersonalAccessToken(self._stub, pat)

    def get(self, token_id: str) -> PersonalAccessToken:
        """Obtain a particular personal access token.

        Args:
            token_id: (str) A unique id of a token object.

        Returns:
            PersonalAccessToken: A token object.

        Typical example:
            client.auth.pats.get("token_id")
        """
        request = pb.TokenRequest()
        request.token_id = token_id
        response = self._stub.GetToken(request)
        return PersonalAccessToken(self._stub, response.token)

    @property
    def maximum_allowed_token_duration(self) -> Duration:
        """Obtain a maximum token duration that can't be exceeded when generating a token.

        Returns:
            Duration.

        Typical example:
            client.auth.pats.maximum_allowed_token_duration
        """
        response = self._stub.GetTokensConfig(Empty())
        return response.maximum_allowed_token_duration

    def __repr__(self):
        return "This class wraps together methods working with Personal Access Tokens (PATs)"
