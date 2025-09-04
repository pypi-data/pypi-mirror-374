from enum import Enum

from ai.h2o.featurestore.api.v1 import CoreService_pb2 as pb


class SearchField(Enum):
    SEARCH_FIELD_FEATURE_NAME = 1
    SEARCH_FIELD_FEATURE_DESCRIPTION = 2
    SEARCH_FIELD_FEATURE_TAG = 3

    @classmethod
    def to_proto(cls, search_field):
        return {
            cls.SEARCH_FIELD_FEATURE_NAME: pb.AdvancedSearchOption.SearchField.SEARCH_FIELD_FEATURE_NAME,
            cls.SEARCH_FIELD_FEATURE_DESCRIPTION: pb.AdvancedSearchOption.SearchField.SEARCH_FIELD_FEATURE_DESCRIPTION,
            cls.SEARCH_FIELD_FEATURE_TAG: pb.AdvancedSearchOption.SearchField.SEARCH_FIELD_FEATURE_TAG,
        }[search_field]
