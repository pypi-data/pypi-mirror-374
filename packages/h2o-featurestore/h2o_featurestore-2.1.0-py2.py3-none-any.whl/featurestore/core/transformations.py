import os
import shutil
import tempfile
from abc import ABC, abstractmethod
from enum import Enum

import requests

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub

from .utils import Utils


class Transformation(ABC):
    @abstractmethod
    def _initialize(self, grpc: CoreServiceStub):
        raise NotImplementedError("Method `_initialize` needs to be implemented by the child class")

    @abstractmethod
    def _to_proto(self):
        raise NotImplementedError("Method `to_proto` needs to be implemented by the child class")

    @staticmethod
    def from_proto(proto: pb.Transformation):
        if proto.HasField("mojo"):
            mojo = DriverlessAIMOJO(None)
            mojo.mojo_remote_location = proto.mojo.filename
            return mojo
        elif proto.HasField("spark_pipeline"):
            spark_pipeline = SparkPipeline(None)
            spark_pipeline.pipeline_remote_location = proto.spark_pipeline.filename
            return spark_pipeline
        elif proto.HasField("join"):
            return JoinFeatureSets(
                proto.join.left_key, proto.join.right_key, JoinFeatureSetsType._from_proto(proto.join.join_type)
            )


class DriverlessAIMOJO(Transformation):
    def __init__(self, mojo_local_location):
        self.mojo_local_location = mojo_local_location
        self.mojo_remote_location = None

    def _initialize(self, grpc: CoreServiceStub):
        if self.mojo_remote_location is None:
            if not os.path.exists(self.mojo_local_location):
                raise Exception(f"Provided file ${self.mojo_local_location} doesn't exists.")

            md5_checksum = Utils.generate_md5_checksum(self.mojo_local_location)
            upload_response = grpc.GenerateTransformationUpload(
                pb.GenerateTransformationUploadRequest(
                    transformation_type=pb.TransformationType.TransformationMojo,
                    md5_checksum=md5_checksum,
                )
            )
            with open(self.mojo_local_location, "rb") as mojo_file:
                response = requests.put(
                    url=upload_response.url,
                    data=mojo_file,
                    headers=upload_response.headers,
                )
                if response.status_code not in range(200, 300):
                    raise Exception(
                        f"DriverlessAIMOJO file upload failed with status code {response.status_code} "
                        f"and message {response.text}"
                    )
                self.mojo_remote_location = upload_response.filename

    def _to_proto(self):
        return pb.Transformation(mojo=pb.MojoTransformation(filename=self.mojo_remote_location))


class SparkPipeline(Transformation):
    def __init__(self, pipeline):
        if pipeline:
            if isinstance(pipeline, str) and pipeline.endswith(".zip"):
                if not os.path.exists(pipeline):
                    raise Exception(f"Provided file {pipeline} doesn't exists.")
                self.pipeline_local_location = pipeline
            elif isinstance(pipeline, str):
                shutil.make_archive("pipeline", "zip", pipeline)
                self.pipeline_local_location = "pipeline.zip"
            else:
                if Utils.is_running_on_databricks():
                    import random
                    import string

                    output_dir = "/tmp/" + "".join((random.choice(string.ascii_lowercase) for x in range(10)))
                    remote_output_dir = "/dbfs" + output_dir
                else:
                    output_dir = tempfile.mkdtemp()
                    remote_output_dir = output_dir
                pipeline.write().overwrite().save(output_dir)
                shutil.make_archive("pipeline", "zip", remote_output_dir)
                shutil.rmtree(remote_output_dir)
                self.pipeline_local_location = "pipeline.zip"
        else:
            self.pipeline_local_location = pipeline
        self.pipeline_remote_location = None

    def _initialize(self, grpc: CoreServiceStub):
        if self.pipeline_remote_location is None:
            md5_checksum = Utils.generate_md5_checksum(self.pipeline_local_location)
            upload_response = grpc.GenerateTransformationUpload(
                pb.GenerateTransformationUploadRequest(
                    transformation_type=pb.TransformationType.TransformationSparkPipeline,
                    md5_checksum=md5_checksum,
                )
            )

            with open(self.pipeline_local_location, "rb") as spark_pipeline_file:
                response = requests.put(
                    url=upload_response.url,
                    data=spark_pipeline_file,
                    headers=upload_response.headers,
                )
                if response.status_code not in range(200, 300):
                    raise Exception(
                        f"SparkPipeline file upload failed with status code {response.status_code} "
                        f"and message {response.text}"
                    )
                self.pipeline_remote_location = upload_response.filename

    def _to_proto(self):
        return pb.Transformation(spark_pipeline=pb.SparkPipelineTransformation(filename=self.pipeline_remote_location))


class JoinFeatureSetsType(Enum):
    INNER = 0
    LEFT = 1
    RIGHT = 2
    FULL = 3
    CROSS = 4

    def _to_proto(self):
        return pb.JoinType.Value("JOIN_TYPE_" + self.name)

    @classmethod
    def _from_proto(cls, join_type: pb.JoinType):
        if join_type == pb.JOIN_TYPE_INNER:
            return JoinFeatureSetsType.INNER
        elif join_type == pb.JOIN_TYPE_LEFT:
            return JoinFeatureSetsType.LEFT
        elif join_type == pb.JOIN_TYPE_RIGHT:
            return JoinFeatureSetsType.RIGHT
        elif join_type == pb.JOIN_TYPE_FULL:
            return JoinFeatureSetsType.FULL
        elif join_type == pb.JOIN_TYPE_CROSS:
            return JoinFeatureSetsType.CROSS
        else:
            raise Exception("Unsupported join_type" + str(join_type))


class JoinFeatureSets(Transformation):
    def __init__(self, left_key, right_key, join_type: JoinFeatureSetsType = JoinFeatureSetsType.INNER):
        self.left_key = left_key
        self.right_key = right_key
        self.join_type = join_type

    def _initialize(self, grpc: CoreServiceStub):
        pass

    def _to_proto(self):
        return pb.Transformation(
            join=pb.JoinTransformation(
                left_key=self.left_key,
                right_key=self.right_key,
                join_type=self.join_type._to_proto(),
            )
        )
