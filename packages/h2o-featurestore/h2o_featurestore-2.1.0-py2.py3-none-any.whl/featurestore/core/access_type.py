from enum import Enum

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb


class AccessType(Enum):
    OWNER = 1
    EDITOR = 2
    CONSUMER = 3
    SENSITIVE_CONSUMER = 4
    VIEWER = 5

    @classmethod
    def from_proto_permission(cls, proto_permission_type):
        return {
            pb.PermissionType.Owner: cls.OWNER,
            pb.PermissionType.Editor: cls.EDITOR,
            pb.PermissionType.Consumer: cls.CONSUMER,
            pb.PermissionType.SensitiveConsumer: cls.SENSITIVE_CONSUMER,
            pb.PermissionType.Viewer: cls.VIEWER,
        }[proto_permission_type]

    @classmethod
    def to_proto_permission(cls, access_type):
        return {
            cls.OWNER: pb.PermissionType.Owner,
            cls.EDITOR: pb.PermissionType.Editor,
            cls.CONSUMER: pb.PermissionType.Consumer,
            cls.SENSITIVE_CONSUMER: pb.PermissionType.SensitiveConsumer,
            cls.VIEWER: pb.PermissionType.Viewer,
        }[access_type]

    @classmethod
    def from_proto_active_permission(cls, active_permission):
        return {
            pb.ACTIVE_PERMISSION_NONE: None,
            pb.ACTIVE_PERMISSION_OWNER: cls.OWNER,
            pb.ACTIVE_PERMISSION_EDITOR: cls.EDITOR,
            pb.ACTIVE_PERMISSION_CONSUMER: cls.CONSUMER,
            pb.ACTIVE_PERMISSION_SENSITIVE_CONSUMER: cls.SENSITIVE_CONSUMER,
            pb.ACTIVE_PERMISSION_VIEWER: cls.VIEWER,
        }[active_permission]

    @classmethod
    def to_proto_active_permission(cls, active_permission):
        return {
            None: pb.ACTIVE_PERMISSION_NONE,
            cls.OWNER: pb.ACTIVE_PERMISSION_OWNER,
            cls.EDITOR: pb.ACTIVE_PERMISSION_EDITOR,
            cls.CONSUMER: pb.ACTIVE_PERMISSION_CONSUMER,
            cls.SENSITIVE_CONSUMER: pb.ACTIVE_PERMISSION_SENSITIVE_CONSUMER,
            cls.VIEWER: pb.ACTIVE_PERMISSION_VIEWER,
        }[active_permission]
