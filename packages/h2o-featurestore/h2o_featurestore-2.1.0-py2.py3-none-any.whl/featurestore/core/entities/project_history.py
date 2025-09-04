import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..utils import Utils
from .user import User


class ProjectHistory:
    """Wrapper around internal project history.

    Typical example:
        for record in project.history:
          print(record)
    """

    def __init__(self, project_history):
        self._history = project_history

    @property
    def action(self):
        return pb.ProjectChange.Name(self._history.action)

    @property
    def performed_by(self):
        return User(self._history.performed_by)

    @property
    def performed_at(self):
        return Utils.proto_to_dict(self._history.project).get(self._performed_at_source())

    def _performed_at_source(self):
        if self._history.action == pb.ProjectChange.Value("PROJECT_CREATED"):
            return "created_date_time"
        else:
            return "last_update_date_time"

    @property
    def project(self):
        from .project import Project

        return Project(None, None, self._history.project)

    def __repr__(self):
        return Utils.pretty_print_proto(self._history)

    def __str__(self):
        return (
            f"Action        : {self.action}\n"
            f"Performed at  : {self.performed_at}\n"
            f"Performed by  : \n{Utils.output_indent_spacing(str(self.performed_by), '  ')}"
            f"Project state : \n{Utils.output_indent_spacing(str(self.project), '  ')}"
        )
