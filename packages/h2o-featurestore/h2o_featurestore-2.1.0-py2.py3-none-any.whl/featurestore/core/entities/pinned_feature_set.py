import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..utils import Utils
from .feature_set import FeatureSet


class PinnedFeatureSet:
    def __init__(self, stub, rest_stub, pinned_feature_set):
        self._stub = stub
        self._rest_stub = rest_stub
        self._pinned_feature_set = pinned_feature_set

    @property
    def name(self):
        return self._pinned_feature_set.feature_set_name

    @property
    def description(self):
        return self._pinned_feature_set.feature_set_description

    @property
    def updated_at(self):
        return Utils.timestamp_to_string(self._pinned_feature_set.updated_at)

    @property
    def pinned_at(self):
        return Utils.timestamp_to_string(self._pinned_feature_set.pinned_at)

    def get_feature_set(self):
        request = pb.FeatureSetRequestId(feature_set_id=self._pinned_feature_set.feature_set_id)
        response = self._stub.GetFeatureSetById(request)
        return FeatureSet(self._stub, self._rest_stub, response.feature_set)

    def __repr__(self):
        return Utils.pretty_print_proto(self._pinned_feature_set)
