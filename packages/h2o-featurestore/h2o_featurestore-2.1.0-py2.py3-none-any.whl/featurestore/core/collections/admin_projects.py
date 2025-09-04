from typing import Iterator

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..access_type import AccessType
from ..entities.project import Project


class AdminProjects:
    def __init__(self, stub, rest_stub):
        self._stub = stub
        self._rest_stub = rest_stub

    def list(self, user_email: str, required_permission: AccessType = None) -> Iterator[Project]:
        """List all available projects as an administrator.

        Args:
            user_email: (str) A User email to search projects for
            required_permission: (AccessType) The required permission to list projects.
                If None, all projects are returned regardless of permissions.

        Returns:
            Generator of all projects

        Typical example:
            client.projects.list(user_email="bob@h2o.ai", required_permission=AccessType.OWNER)

        For more details:
            https://docs.h2o.ai/featurestore/api/admin_api.html#listing-projects
        """
        request = pb.AdminProjectSearchRequest()
        request.user_email = user_email
        request.required_permission = AccessType.to_proto_active_permission(required_permission)
        while request:
            response = self._stub.AdminSearchProjects(request)
            if response.next_page_token:
                request = pb.AdminProjectSearchRequest()
                request.page_token = response.next_page_token
            else:
                request = None
            for project in response.listable_project:
                yield Project(self._stub, self._rest_stub, project)
