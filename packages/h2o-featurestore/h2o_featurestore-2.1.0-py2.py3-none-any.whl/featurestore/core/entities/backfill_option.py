import datetime
from typing import Optional

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..transformations import SparkPipeline
from ..utils import Utils


class BackfillOption:
    def __init__(
        self,
        from_version: str,
        from_date: Optional[datetime.datetime] = None,
        to_date: Optional[datetime.datetime] = None,
        spark_pipeline: Optional[SparkPipeline] = None,
        feature_mapping: Optional[dict] = None,
    ):
        self._from_version = from_version
        self._from_date = from_date
        self._to_date = to_date
        self._spark_pipeline = spark_pipeline
        self._feature_mapping = feature_mapping

    def _to_proto(self, stub):
        if self._spark_pipeline:
            self._spark_pipeline._initialize(stub)
            spark_pipeline = pb.SparkPipelineTransformation(filename=self._spark_pipeline.pipeline_remote_location)
        else:
            spark_pipeline = None
        return pb.BackfillOptions(
            from_date=Utils.date_time_to_proto_timestamp(self._from_date),
            to_date=Utils.date_time_to_proto_timestamp(self._to_date),
            from_version=self._from_version,
            spark_pipeline=spark_pipeline,
            feature_mapping=self._feature_mapping,
        )
