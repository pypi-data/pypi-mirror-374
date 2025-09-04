from enum import Enum

from ai.h2o.featurestore.api.v1 import CoreService_pb2 as pb


class SearchOperator(Enum):
    SEARCH_OPERATOR_LIKE = 1
    SEARCH_OPERATOR_EQ = 2

    @classmethod
    def to_proto(cls, search_operator):
        return {
            cls.SEARCH_OPERATOR_LIKE: pb.AdvancedSearchOption.SearchOperator.SEARCH_OPERATOR_LIKE,
            cls.SEARCH_OPERATOR_EQ: pb.AdvancedSearchOption.SearchOperator.SEARCH_OPERATOR_EQ,
        }[search_operator]
