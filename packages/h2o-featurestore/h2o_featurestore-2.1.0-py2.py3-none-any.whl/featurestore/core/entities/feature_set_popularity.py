import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..access_type import AccessType
from ..utils import Utils
from .feature_set import FeatureSet


class FeatureSetPopularity:
    def __init__(self, stub, rest_stub, popular_feature_set):
        self._stub = stub
        self._rest_stub = rest_stub
        self._popular_feature_set = popular_feature_set

    @property
    def name(self):
        return self._popular_feature_set.feature_set_name

    @property
    def description(self):
        return self._popular_feature_set.feature_set_description

    @property
    def number_of_retrievals(self):
        return self._popular_feature_set.number_of_retrievals

    @property
    def current_permission(self):
        return AccessType.from_proto_active_permission(self._popular_feature_set.permission)

    def get_feature_set(self):
        request = pb.FeatureSetRequestId(feature_set_id=self._popular_feature_set.feature_set_id)
        response = self._stub.GetFeatureSetById(request)
        return FeatureSet(self._stub, self._rest_stub, response.feature_set)

    def __repr__(self):
        return Utils.pretty_print_proto(self._popular_feature_set)
