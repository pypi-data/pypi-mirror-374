import time

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub

from ..entities.scheduled_task import ScheduledTask
from ..job_info import JobInfo


class ScheduledTasks:
    def __init__(self, stub: CoreServiceStub, feature_set):
        self._stub = stub
        self._feature_set = feature_set

    def create_ingest_task(self, request: pb.ScheduleTaskRequest):
        response = self._stub.ScheduleIngestJob(request)
        return ScheduledTask(self._stub, response.task)

    def create_lazy_ingest_task(self, request: pb.ScheduleTaskRequest):
        response = self._stub.ScheduleLazyIngestTask(request)
        return ScheduledTask(self._stub, response.task)

    def tasks(self):
        """List scheduled tasks.

        Returns:
            Generator of scheduled tasks

        Typical example:
            fs.schedule.tasks()

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_schedule.html#to-list-scheduled-tasks
        """
        request = pb.ListScheduledTasksRequest()
        request.feature_set_id = self._feature_set.id
        while request:
            response = self._stub.ListScheduledTasks(request)
            if response.next_page_token:
                request.page_token = response.next_page_token
            else:
                request = None
            for task in response.tasks:
                yield ScheduledTask(self._stub, task)

    def get(self, task_id: str):
        """Obtain a scheduled task.

        Args:
            task_id: (str) A unique id of a scheduled task.

        Returns:
            ScheduledTask: An existing scheduled task.

        Typical example:
            task = fs.schedule.get("task_id")
        """
        request = pb.ScheduledTaskId(scheduled_task_id=task_id)
        response = self._stub.GetScheduledTask(request)
        return ScheduledTask(self._stub, response.task)

    def get_lazy_ingest_task(self):
        """Obtain a lazy ingest task.

        This retrieves an existing ingest task which is planned for later ingestion.
        Each major version of a feature set can only contain one lazy ingest task.

        Returns:
            ScheduledTask: A scheduled task.

        Typical example:
            task = fs.schedule.get_lazy_ingest_task()
        """
        request = pb.GetLazyIngestTaskRequest(
            feature_set_id=self._feature_set.id, feature_set_version=self._feature_set.version
        )
        response = self._stub.GetLazyIngestTask(request)
        return ScheduledTask(self._stub, response.task)

    def start_lazy_ingest_task(self):
        """Starts a lazy ingest task."""
        request = pb.LazyIngestRequest(
            feature_set_id=self._feature_set.id, feature_set_version=self._feature_set.version
        )
        response = self._stub.StartLazyIngestTask(request)
        if response.job_id:
            info = JobInfo(self._stub, response.job_id)
            while not self._get_job(response.job_id).done:
                info.show_progress()
                time.sleep(2)
            info.show_progress()  # there is possibility that some progress was pushed before finishing job

    def _get_job(self, job_id):
        return self._stub.GetJob(job_id)
