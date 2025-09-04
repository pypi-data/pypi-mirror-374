import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..utils import Utils
from .project import Project


class RecentlyUsedProject:
    def __init__(self, stub, rest_stub, recently_used_project):
        self._stub = stub
        self._rest_stub = rest_stub
        self._recently_used_project = recently_used_project

    @property
    def name(self):
        return self._recently_used_project.project_name

    @property
    def description(self):
        return self._recently_used_project.project_description

    @property
    def updated_at(self):
        return Utils.timestamp_to_string(self._recently_used_project.updated_at)

    @property
    def last_access_at(self):
        return Utils.timestamp_to_string(self._recently_used_project.last_access_at)

    def get_project(self):
        request = pb.GetProjectRequest(project_name=self._recently_used_project.project_name)
        response = self._stub.GetProject(request)
        return Project(self._stub, self._rest_stub, response.project)

    def __repr__(self):
        return Utils.pretty_print_proto(self._recently_used_project)
