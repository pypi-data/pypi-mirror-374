import logging
from typing import Iterator

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..access_modifier import AccessModifier
from ..entities.feature_set import FeatureSet
from ..entities.project import Project


class Projects:
    def __init__(self, stub, rest_stub, admin_projects):
        self._stub = stub
        self._rest_stub = rest_stub
        self.admin = admin_projects

    def list(self) -> Iterator[Project]:
        """List all available projects.

        Returns:
            Generator of all projects

        Typical example:
            client.projects.list()

        For more details:
            https://docs.h2o.ai/featurestore/api/projects_api.html#listing-projects
        """
        request = pb.ListProjectsPageRequest()
        while request:
            response = self._stub.ListProjectsPage(request)
            if response.next_page_token:
                request = pb.ListProjectsPageRequest()
                request.page_token = response.next_page_token
            else:
                request = None
            for project in response.projects:
                yield Project(self._stub, self._rest_stub, project)

    def list_feature_sets(self, project_names=[]) -> Iterator[FeatureSet]:
        """List feature sets across multiple projects.

        Args:
            project_names: (list[str]) A collection of existing project names.

        Returns:
            Iterator[FeatureSet]: An iterator which obtains the feature sets lazily.

        Typical example:
            client.projects.list_feature_sets(["project_name_A", "project_name_B"])

        For more details:
            https://docs.h2o.ai/featurestore/api/projects_api.html#listing-feature-sets-across-multiple-projects
        """
        request = pb.ListFeatureSetsPageRequest()
        request.project_names.extend(project_names)
        while request:
            response = self._stub.ListFeatureSetsPage(request)
            if response.next_page_token:
                request.page_token = response.next_page_token
            else:
                request = None
            for feature_set in response.feature_sets:
                yield FeatureSet(self._stub, self._rest_stub, feature_set)

    def create(self, project_name: str, description: str = "", access_modifier: AccessModifier = None) -> Project:
        """Create a project.

        Args:
            project_name: (str) A project name.
            description: (str) A description about the project.
            access_modifier: (AccessModifier) If AccessModifier.PUBLIC, project is visible to all users
                                              If AccessModifier.PROJECT_ONLY, only users with viewer permission can list
                                              feature sets within this project.
                                              If AccessModifier.PRIVATE, project is visible only to its owner.

        Returns:
            Project: A new project with specified attributes.

        Typical example:
            project = client.projects.create(project_name="project", description="description",
              access_type=AccessModifier.PUBLIC)

        For more details:
            https://docs.h2o.ai/featurestore/api/projects_api.html#create-a-project
        """
        request = pb.CreateProjectRequest()
        request.access_modifier = AccessModifier.to_proto(access_modifier)
        request.project_name = project_name
        request.description = description
        response = self._stub.CreateProject(request)
        if response.already_exists:
            logging.warning("Project '" + project_name + "' already exists.")
        return Project(self._stub, self._rest_stub, response.project)

    def get(self, project_name: str) -> Project:
        """Obtain an existing project.

        Args:
            project_name: (str) A project name.

        Returns:
            Project: An existing project.

        Typical example:
            project = client.projects.get(project_name="project")
        """
        request = pb.GetProjectRequest()
        request.project_name = project_name
        response = self._stub.GetProject(request)
        return Project(self._stub, self._rest_stub, response.project)

    def __repr__(self):
        return "This class wraps together methods working with projects"
