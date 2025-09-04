from typing import List

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..entities.backfill_job import BackfillJob
from ..entities.base_job import BaseJob
from ..entities.compute_recommendation_classifiers_job import ComputeRecommendationClassifiersJob
from ..entities.compute_statistics_job import ComputeStatisticsJob
from ..entities.extract_schema_job import ExtractSchemaJob
from ..entities.ingest_job import IngestJob
from ..entities.materialization_online_job import MaterializationOnlineJob
from ..entities.optimize_storage_job import OptimizeStorageJob
from ..entities.retrieve_job import RetrieveJob
from ..entities.revert_ingest_job import RevertIngestJob


class Jobs:
    def __init__(self, stub, rest_stub):
        self._stub = stub
        self._rest_stub = rest_stub

    @staticmethod
    def _create_job(stub, rest_stub, job_proto):
        job_id = pb.JobId(job_id=job_proto.job_id)
        if job_proto.job_type == pb.JobType.Ingest:
            return IngestJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.ExtractSchema:
            return ExtractSchemaJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.Retrieve:
            return RetrieveJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.MaterializationOnline:
            return MaterializationOnlineJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.ComputeStatistics:
            return ComputeStatisticsJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.Revert:
            return RevertIngestJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.ComputeRecommendationClassifiers:
            return ComputeRecommendationClassifiersJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.Backfill:
            return BackfillJob(stub, job_id)
        elif job_proto.job_type == pb.JobType.OptimizeStorage:
            return OptimizeStorageJob(stub, job_id)

    def list(self, active=True, job_type=pb.JobType.Unknown) -> List[BaseJob]:
        """Return currently running jobs.

        By default, only active jobs are returned.

        Args:
            active: (bool) If True, allows active jobs.
            job_type: (JobType) Object represents a specific job type.
              INGEST | RETRIEVE | EXTRACT_SCHEMA | REVERT_INGEST | MATERIALIZATION_ONLINE | COMPUTE_STATISTICS |
              COMPUTE_RECOMMENDATION_CLASSIFIERS | BACKFILL | OPTIMIZE_STORAGE

        Returns:
            list[BaseJob]: A collection of jobs.

            For example:

            [Job(id=test123, type=ExtractSchema, done=True, childJobIds=[]),
            Job(id=test456, type=RetrieveJob, done=True, childJobIds=[])]

        Typical example:
            client.jobs.list()
            client.jobs.list(active=False, job_type=INGEST)

        For more details:
            https://docs.h2o.ai/featurestore/api/jobs_api.html#listing-jobs
        """
        request = pb.ListJobsRequest(active=active, job_type=job_type)
        resp = self._stub.ListJobs(request)
        return [Jobs._create_job(self._stub, self._rest_stub, job_proto) for job_proto in resp.jobs]

    def get(self, job_id: str) -> BaseJob:
        """Obtain an existing job.

        Args:
            job_id: (str) A unique id of an existing job.

        Returns:
            BaseJob: A job.

            For example:

            Job(id=test123, type=ExtractSchema, done=True, childJobIds=[])

        Typical example:
            job = client.jobs.get("job_id")

        For more details:
            https://docs.h2o.ai/featurestore/api/jobs_api.html#getting-a-job
        """
        request = pb.JobId(job_id=job_id)
        job_proto = self._stub.GetJob(request)
        return Jobs._create_job(self._stub, self._rest_stub, job_proto)

    def __repr__(self):
        return "This class wraps together methods working with jobs"
