from enum import Enum

import ai.h2o.featurestore.api.v1.FeatureSetProtoApi_pb2 as FeatureSetApi


class FeatureSetFlow(Enum):
    ONLINE_ONLY = 1
    OFFLINE_ONLY = 2
    OFFLINE_ONLINE_MANUAL = 3
    OFFLINE_ONLINE_AUTOMATIC = 4

    @staticmethod
    def _from_proto(flow: FeatureSetApi.FeatureSetFlow):
        if flow == FeatureSetApi.OFFLINE_ONLINE_AUTOMATIC:
            return FeatureSetFlow.OFFLINE_ONLINE_AUTOMATIC
        elif flow == FeatureSetApi.OFFLINE_ONLINE_MANUAL:
            return FeatureSetFlow.OFFLINE_ONLINE_MANUAL
        elif flow == FeatureSetApi.ONLINE_ONLY:
            return FeatureSetFlow.ONLINE_ONLY
        elif flow == FeatureSetApi.OFFLINE_ONLY:
            return FeatureSetFlow.OFFLINE_ONLY
        else:
            raise Exception("Unsupported flow" + str(flow))
