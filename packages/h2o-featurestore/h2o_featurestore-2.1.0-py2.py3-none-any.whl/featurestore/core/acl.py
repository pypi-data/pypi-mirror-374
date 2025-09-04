import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from .entities.permission import ManageablePermission, Permission
from .entities.permission_request import ManageablePermissionRequest, PermissionRequest


class AccessControlList:
    def __init__(self, stub, rest_stub):
        self.requests = AclRequests(stub, rest_stub)
        self.permissions = AclPermissions(stub, rest_stub)


class AclRequests:
    def __init__(self, stub, rest_stub):
        self.projects = AclProjectRequests(stub, rest_stub)
        self.feature_sets = AclFeatureSetsRequests(stub, rest_stub)


class AclPermissions:
    def __init__(self, stub, rest_stub):
        self.projects = AclProjectPermissions(stub, rest_stub)
        self.feature_sets = AclFeatureSetsPermissions(stub, rest_stub)


class AclProjectRequests:
    def __init__(self, stub, rest_stub):
        self._stub = stub
        self._rest_stub = rest_stub

    def list(self):
        """List pending project permission requests.

        Returns:
            Generator of project permission requests

        Typical example:
            my_requests = client.acl.requests.projects.list()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        request = pb.ListPermissionsPageRequest(filters=[pb.PermissionState.PENDING])
        return (
            PermissionRequest(self._stub, self._rest_stub, entry.permission, entry.project.name)
            for entry in paged_response_to_request(request, self._stub.ListProjectPermissionsPage)
        )

    def list_manageable(self):
        """List pending manageable project permission requests.

        Returns:
            Generator of manageable project permission requests

        Typical example:
            manageable_requests = client.acl.requests.projects.list_manageable()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        request = pb.ListPermissionsPageRequest(filters=[pb.PermissionState.PENDING])
        return (
            ManageablePermissionRequest(self._stub, self._rest_stub, entry.permission, entry.project.name)
            for entry in paged_response_to_request(request, self._stub.ListManageableProjectPermissionsPage)
        )


class AclFeatureSetsRequests:
    def __init__(self, stub, rest_stub):
        self._stub = stub
        self._rest_stub = rest_stub

    def list(self):
        """List pending feature set permission requests.

        Returns:
            Generator of feature set permission requests

        Typical example:
            my_requests = client.acl.requests.feature_sets.list()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        request = pb.ListPermissionsPageRequest(filters=[pb.PermissionState.PENDING])
        return (
            PermissionRequest(self._stub, self._rest_stub, entry.permission, entry.feature_set.project_name)
            for entry in paged_response_to_request(request, self._stub.ListFeatureSetsPermissionsPage)
        )

    def list_manageable(self):
        """List pending manageable feature set permission requests.

        Returns:
            Generator of manageable feature set permission requests

        Typical example:
            manageable_requests = client.acl.requests.feature_sets.list_manageable()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        request = pb.ListPermissionsPageRequest(filters=[pb.PermissionState.PENDING])
        return (
            ManageablePermissionRequest(self._stub, self._rest_stub, entry.permission, entry.feature_set.project_name)
            for entry in paged_response_to_request(request, self._stub.ListManageableFeatureSetsPermissionsPage)
        )


class AclProjectPermissions:
    def __init__(self, stub, rest_stub):
        self._stub = stub
        self._rest_stub = rest_stub

    def list(self, filters=None):
        """List existing project permission requests.

        Args:
            filters: (list[PermissionState]) Filter includes the state of permission (either REJECTED or GRANTED).

        Returns:
            Generator of project permissions

        Typical example:
            filters = [PermissionState.REJECTED]
            my_requests = client.acl.requests.projects.list(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#requesting-permissions-to-a-project
        """
        if filters is None:
            filters = [pb.PermissionState.GRANTED]
        request = pb.ListPermissionsPageRequest(filters=filters)
        return (
            Permission(self._stub, self._rest_stub, entry.permission, entry.project.name)
            for entry in paged_response_to_request(request, self._stub.ListProjectPermissionsPage)
        )

    def list_manageable(self, filters=None):
        """List pending manageable project permission requests.

        Args:
            filters: (list[PermissionState]) Filter includes the state of permission (either REJECTED or GRANTED).

        Returns:
            Generator of manageable project permissions

        Typical example:
            filters = [PermissionState.REJECTED]
            manageable_requests = client.acl.requests.projects.list_manageable(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        if filters is None:
            filters = [pb.PermissionState.GRANTED]
        request = pb.ListPermissionsPageRequest(filters=filters)
        return (
            ManageablePermission(self._stub, self._rest_stub, entry.permission, entry.project.name)
            for entry in paged_response_to_request(request, self._stub.ListManageableProjectPermissionsPage)
        )


class AclFeatureSetsPermissions:
    def __init__(self, stub, rest_stub):
        self._stub = stub
        self._rest_stub = rest_stub

    def list(self, filters=None):
        """List pending feature set permission requests.

        Args:
            filters: (list[PermissionState]) Filter includes the state of permission (either REJECTED or GRANTED).

        Returns:
            Generator of feature set permissions

        Typical example:
            filters = [PermissionState.REJECTED]
            my_requests = client.acl.requests.feature_sets.list(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-feature-set-permissions
        """
        if filters is None:
            filters = [pb.PermissionState.GRANTED]
        request = pb.ListPermissionsPageRequest(filters=filters)
        return (
            Permission(self._stub, self._rest_stub, entry.permission, entry.feature_set.project_name)
            for entry in paged_response_to_request(request, self._stub.ListFeatureSetsPermissionsPage)
        )

    def list_manageable(self, filters=None):
        """List pending manageable feature set permission requests.

        Args:
            filters: (list[PermissionState]) Filter includes the state of permission (either REJECTED or GRANTED).

        Returns:
            Generator of manageable feature set permissions

        Typical example:
            filters = [PermissionState.REJECTED]
            manageable_requests = client.acl.requests.feature_sets.list_manageable(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-feature-set-permissions
        """
        if filters is None:
            filters = [pb.PermissionState.GRANTED]
        request = pb.ListPermissionsPageRequest(filters=filters)
        return (
            ManageablePermission(self._stub, self._rest_stub, entry.permission, entry.feature_set.project_name)
            for entry in paged_response_to_request(request, self._stub.ListManageableFeatureSetsPermissionsPage)
        )


def paged_response_to_request(request, core_call):
    while request:
        response = core_call(request)
        if response.next_page_token:
            request.page_token = response.next_page_token
        else:
            request = None
        for entry in response.entries:
            yield entry
