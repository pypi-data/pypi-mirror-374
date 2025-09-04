import logging

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..access_type import AccessType
from ..utils import Utils
from .feature_set import FeatureSet
from .project import Project


class PermissionBase:
    def __init__(self, stub, rest_stub, permission, project_name=None):
        self._permission = permission
        self._stub = stub
        self._rest_stub = rest_stub
        self._project_name = project_name

    @property
    def access_type(self):
        return AccessType.from_proto_permission(self._permission.permission)

    @property
    def status(self):
        return pb.PermissionState.Name(self._permission.state)

    @property
    def resource_id(self):
        return self._permission.resource_id

    @property
    def resource_type(self):
        return pb.ResourceType.Name(self._permission.resource_type)

    @property
    def reason(self):
        return self._permission.creation_reason

    @property
    def created_on(self):
        return Utils.timestamp_to_string(self._permission.created_on)

    @property
    def last_update_on(self):
        return Utils.timestamp_to_string(self._permission.last_update_on)

    def get_resource(self):
        """Get a resource (project or feature set) of the request.

        Returns:
            Project | FeatureSet: A corresponding project or feature set.

        Typical example:
            manageable_request.get_resource()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        if self._permission.resource_type == pb.ResourceType.PROJECT:
            request = pb.GetProjectRequest(project_name=self._project_name)
            response = self._stub.GetProject(request)
            return Project(self._stub, self._rest_stub, response.project)
        elif self._permission.resource_type == pb.ResourceType.FEATURE_SET:
            request = pb.FeatureSetRequestId(feature_set_id=self._permission.resource_id)
            response = self._stub.GetFeatureSetById(request)
            return FeatureSet(self._stub, self._rest_stub, response.feature_set)
        else:
            logging.error("Unknown resource type")

    def __repr__(self):
        return Utils.pretty_print_proto(self._permission)
