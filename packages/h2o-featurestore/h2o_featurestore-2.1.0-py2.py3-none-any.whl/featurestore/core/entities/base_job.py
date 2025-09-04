import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub

from ..job_info import JobInfo


class BaseJob(ABC):
    def __init__(self, stub: CoreServiceStub, job_id):
        self._stub = stub
        self._job_id = job_id
        self._result = None
        self._job = self._stub.GetJob(self._job_id)
        self._thread_pool = ThreadPoolExecutor(5)
        self._info = JobInfo(self._stub, self._job_id)

    @property
    def id(self):
        return self._job_id.job_id

    @property
    def job_type(self):
        return pb.JobType.Name(self._job.job_type)

    @property
    def done(self):
        return self.is_done()

    @property
    def child_job_ids(self):
        return self._job.childJobIds

    @abstractmethod
    def _response_method(self, job_id):
        raise NotImplementedError("Method `_response_method` needs to be implemented by the child class")

    def is_done(self) -> bool:
        """Job status (whether completed or not)."""
        return self._stub.GetJob(self._job_id).done

    def is_cancelled(self) -> bool:
        """Job status (whether is cancelled or not)."""
        return self._stub.GetJob(self._job_id).cancelled

    def cancel(self, wait_for_completion=False):
        """Request job cancellation."""
        if not self.is_done():
            self._stub.CancelJob(self._job_id)
            if wait_for_completion:
                self.wait_for_result()

    def wait_for_result(self):
        """Return job results after completion."""
        while not self.is_done():
            self.show_progress()
            time.sleep(2)
        self.show_progress()  # there is possibility that some progress was pushed before finishing job
        return self.get_result()

    def get_result(self):
        """A job results."""
        if not self._result:
            if not self.is_done():
                raise Exception("Job has not finished yet!")
            if not self.is_cancelled():
                self._result = self._response_method(self._job_id)
            else:
                self._result = None
        return self._result

    def show_progress(self):
        """Retrieve job progress."""
        self._info.show_progress()

    def get_metrics(self):
        """Completed metrics of a job."""
        return self._info.get_metrics()

    def __repr__(self):
        return f"""Job(id={self.id}, type={self.job_type}, done={self.done}, childJobIds={self.child_job_ids})"""
