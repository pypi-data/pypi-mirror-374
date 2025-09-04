from abc import ABC, abstractmethod

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub

from .utils import Utils


class StorageOptimization(ABC):
    @abstractmethod
    def _initialize(self, grpc: CoreServiceStub):
        raise NotImplementedError("Method `_initialize` needs to be implemented by the child class")

    @abstractmethod
    def _to_proto(self):
        raise NotImplementedError("Method `to_proto` needs to be implemented by the child class")

    @staticmethod
    def from_proto(proto: pb.StorageOptimization):
        if proto.HasField("compact"):
            return CompactOptimization()
        elif proto.HasField("z_order_by"):
            columns = proto.z_order_by.columns
            return ZOrderByOptimization(columns)
        else:
            return None

    def __repr__(self):
        return Utils.pretty_print_proto(self._to_proto())


class ZOrderByOptimization(StorageOptimization):
    def __init__(self, columns):
        self.columns = columns

    def _initialize(self, grpc: CoreServiceStub):
        pass

    def _to_proto(self):
        spec = pb.OptimizeStorageZOrderBySpec(columns=self.columns)
        proto = pb.StorageOptimization()
        proto.z_order_by.CopyFrom(spec)
        return proto


class CompactOptimization(StorageOptimization):
    def __init__(self):
        pass

    def _initialize(self, grpc: CoreServiceStub):
        pass

    def _to_proto(self):
        spec = pb.OptimizeStorageCompactSpec()
        proto = pb.StorageOptimization()
        proto.compact.CopyFrom(spec)
        return proto
