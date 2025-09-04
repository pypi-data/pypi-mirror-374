import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..access_type import AccessType
from ..utils import Utils
from .user import User


class UserWithPermission:
    def __init__(self, user_with_permission):
        self._user_with_permission = user_with_permission

    @property
    def user(self):
        return User(self._user_with_permission.user)

    @property
    def access_type(self):
        return AccessType.from_proto_permission(self._user_with_permission.resource_permission.permission)

    @property
    def resource_type(self):
        return pb.ResourceType.Name(self._user_with_permission.resource_permission.resource_type)

    def __repr__(self):
        return Utils.pretty_print_proto(self._user_with_permission)

    def __str__(self):
        return (
            f"User\n{Utils.output_indent_spacing(str(self.user), '  ')}"
            f"Access Type   : {self.access_type}\n"
            f"Resource Type : {self.resource_type}\n"
        )
