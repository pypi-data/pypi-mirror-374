from enum import Enum

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb


class AccessModifier(Enum):
    PUBLIC = 1
    PROJECT_ONLY = 2
    PRIVATE = 3

    @classmethod
    def from_proto(cls, proto_access_modifier):
        return {
            pb.AccessModifier.ACCESS_MODIFIER_PUBLIC: cls.PUBLIC,
            pb.AccessModifier.ACCESS_MODIFIER_PROJECT_ONLY: cls.PROJECT_ONLY,
            pb.AccessModifier.ACCESS_MODIFIER_PRIVATE: cls.PRIVATE,
        }[proto_access_modifier]

    @classmethod
    def to_proto(cls, access_modifier):
        return {
            cls.PUBLIC: pb.AccessModifier.ACCESS_MODIFIER_PUBLIC,
            cls.PROJECT_ONLY: pb.AccessModifier.ACCESS_MODIFIER_PROJECT_ONLY,
            cls.PRIVATE: pb.AccessModifier.ACCESS_MODIFIER_PRIVATE,
            None: pb.AccessModifier.ACCESS_MODIFIER_UNSPECIFIED,
        }[access_modifier]
