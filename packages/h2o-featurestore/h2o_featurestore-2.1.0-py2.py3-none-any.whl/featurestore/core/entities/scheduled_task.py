import json
import logging

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..utils import Utils
from .task_execution_history import TaskExecutionHistory


class ScheduledTask:
    def __init__(self, stub, scheduled_task):
        st = pb.ScheduledTask()
        st.CopyFrom(scheduled_task)
        self._scheduled_task = st
        self._stub = stub

    @property
    def id(self):
        return self._scheduled_task.id

    @property
    def name(self):
        return self._scheduled_task.name

    @property
    def description(self):
        return self._scheduled_task.description

    @description.setter
    def description(self, value: str):
        update_request = pb.ScheduledTaskUpdateRequest(
            scheduled_task_id=self._scheduled_task.id,
            description=value,
            updated_fields=["description"],
        )
        self._stub.UpdateScheduledTask(update_request)
        self._refresh()

    @property
    def schedule(self):
        return self._scheduled_task.schedule

    @schedule.setter
    def schedule(self, value: str):
        update_request = pb.ScheduledTaskUpdateRequest(
            scheduled_task_id=self._scheduled_task.id,
            schedule=value,
            updated_fields=["schedule"],
        )
        self._stub.UpdateScheduledTask(update_request)
        self._refresh()

    def delete(self):
        """Delete a scheduled task."""
        request = pb.ScheduledTaskId(scheduled_task_id=self._scheduled_task.id)
        self._stub.DeleteScheduledTask(request)

    def _refresh(self):
        request = pb.ScheduledTaskId(scheduled_task_id=self._scheduled_task.id)
        response = self._stub.GetScheduledTask(request)
        self._scheduled_task = response.task

    def execution_history(self):
        """Get information about executions of this scheduled task."""
        request = pb.ListScheduledTaskExecutionsRequest(scheduled_task_id=self._scheduled_task.id)
        while request:
            response = self._stub.ListScheduledTaskExecutionHistory(request)
            if response.next_page_token:
                request = pb.ListScheduledTaskExecutionsRequest(scheduled_task_id=self._scheduled_task.id)
                request.page_token = response.next_page_token
            else:
                request = None
            for execution_record in response.execution_history:
                yield TaskExecutionHistory(execution_record)

    def is_paused(self):
        self._refresh()
        return self._scheduled_task.next_run_time.seconds == 0

    def pause(self):
        """Pause scheduled task."""
        if self.is_paused():
            logging.warning("pause() call ignored as task is already paused")
            return
        request = pb.PauseScheduledTaskRequest(scheduled_task_id=self._scheduled_task.id)
        self._stub.PauseScheduledTask(request)
        self._refresh()

    def resume(self, allowed_failures=None):
        """Resume a scheduled task and set an allowed number of failures.

        If the allowed_failures is a negative number then it means that the failures are not tracked.
        """
        if not self.is_paused():
            logging.warning("resume() call ignored as task is already scheduled")
            return

        setup_failures = allowed_failures is not None
        if setup_failures and allowed_failures < 0:
            allowed_failures = -1

        request = pb.ResumeScheduledTaskRequest(
            scheduled_task_id=self._scheduled_task.id,
            setup_failures=setup_failures,
            allowed_failures=allowed_failures,
        )
        self._stub.ResumeScheduledTask(request)
        self._refresh()

    @property
    def allowed_failures(self):
        if self._scheduled_task.allowed_failures >= 0:
            return str(self._scheduled_task.allowed_failures)
        else:
            return "unlimited"

    def __repr__(self):
        task_type = pb.TaskType.DESCRIPTOR.values_by_number.get(self._scheduled_task.task_type).name
        task = {
            "id": self._scheduled_task.id,
            "name": self._scheduled_task.name,
            "description": self._scheduled_task.description,
            "feature_set_id": self._scheduled_task.feature_set_id,
            "project_id": self._scheduled_task.project_id,
            "source": json.loads(Utils.pretty_print_proto(self._scheduled_task.source)),
            "schedule": self._scheduled_task.schedule,
            "next_run_time": _real_timestamp_to_string(self._scheduled_task.next_run_time),
            "last_exec": _real_timestamp_to_string(self._scheduled_task.last_exec),
            "owner": json.loads(Utils.pretty_print_proto(self._scheduled_task.owner)),
            "created_date_time": Utils.convert_timestamp_to_str_with_zone(self._scheduled_task.created_date_time),
            "last_update_date_time": _real_timestamp_to_string(self._scheduled_task.last_update_date_time),
            "task_type": task_type,
            "feature_set_version": self._scheduled_task.feature_set_version,
            "allowed_failures": self.allowed_failures,
        }
        return json.dumps(task, indent=2)

    def __str__(self):
        return (
            f"Name                  : {self.name} \n"
            f"Description           : {self.description} \n"
            f"Feature set version   : {self._scheduled_task.feature_set_version} \n"
            f"Owner                   \n{self._custom_user_string()}"
            f"Source                  \n{self._custom_source_string()}"
            f"Schedule              : {self.schedule} \n"
            f"Last execution        : {_real_timestamp_to_string(self._scheduled_task.last_exec)} \n"
            f"Next run time         : {_real_timestamp_to_string(self._scheduled_task.next_run_time)}"
        )

    def _custom_user_string(self):
        return (
            f"          Name        : {self._scheduled_task.owner.name} \n"
            f"          Email       : {self._scheduled_task.owner.email} \n"
        )

    def _custom_source_string(self):
        source_dict = Utils.proto_to_dict(self._scheduled_task.source)
        source = list(source_dict.keys())[0]
        tmp_str = ""
        for key, value in source_dict.get(source).items():
            tmp_str = tmp_str + Utils.output_indent_spacing(f"{key}: {value} \n", "           ")

        return (
            f"{Utils.output_indent_spacing(source, '       ')}: [ \n"
            f"{tmp_str}"
            f"{Utils.output_indent_spacing(']', '       ')} \n"
        )


def _real_timestamp_to_string(timestamp):
    if timestamp.seconds == 0:
        return ""
    else:
        return Utils.convert_timestamp_to_str_with_zone(timestamp)
