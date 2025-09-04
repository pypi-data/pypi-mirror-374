import re
from typing import Optional

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub

from ...rest_stub import RestStub
from ..entities.advanced_search_option import AdvancedSearchOption
from ..entities.feature_set import FeatureSet
from ..feature_set_flow import FeatureSetFlow
from ..schema import Schema
from ..utils import Utils


class FeatureSets:
    def __init__(self, stub: CoreServiceStub, rest_stub: RestStub, project):
        self._project = project
        self._stub = stub
        self._rest_stub = rest_stub

    def register(
        self,
        schema,
        feature_set_name,
        description="",
        primary_key=None,
        time_travel_column=None,
        time_travel_column_format="yyyy-MM-dd HH:mm:ss",
        partition_by=None,
        time_travel_column_as_partition=False,
        flow: Optional[FeatureSetFlow] = None,
    ):
        """Create a new feature set.

        Args:
            schema: (Schema) A schema that contains feature columns and data types.
            feature_set_name: (str) A name for the feature set.
            description: (str) A description about the feature set.
            primary_key: (str | list[str]) A key / keys for a feature column name.
            time_travel_column: (str) A feature column in a schema.
            time_travel_column_format: (str) Format for time travel column.
            partition_by: (list[str]) Object represents a list of String.
            time_travel_column_as_partition: (bool) Feature Store uses time travel column for data partitioning.
            flow: (FeatureSetFlow) Feature store uses flow to control where data lives (offline, online or both)

        Returns:
            FeatureSet: A new feature set with specified attributes.

        Typical example:
            project.feature_sets.register(schema, "feature_set_name", description="", primary_key=None,
              time_travel_column=None, time_travel_column_format="yyyy-MM-dd HH:mm:ss", partition_by=None,
              time_travel_column_as_partition=False)

        Raises:
            ValueError: Parameter schema should be of type Schema.

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#registering-a-feature-set
        """
        if not isinstance(schema, Schema):
            raise ValueError("Parameter `schema` should be of type `featurestore.core.schema.Schema`")
        request = pb.RegisterFeatureSetRequest()
        request.schema.extend(schema._to_proto_schema())
        request.project.CopyFrom(self._project)
        if schema.derivation is not None:
            schema.derivation.transformation._initialize(self._stub)
            request.derived_from.CopyFrom(schema.derivation._to_proto())
        if primary_key is not None:
            if isinstance(primary_key, str):
                request.primary_key.append(primary_key)
            else:
                request.primary_key.extend(primary_key)
        if time_travel_column is not None:
            request.time_travel_column = time_travel_column
        request.description = description
        if partition_by is not None:
            request.partition_by.extend(partition_by)
        request.time_travel_column_as_partition = time_travel_column_as_partition
        request.time_travel_column_format = time_travel_column_format
        request.feature_set_name = feature_set_name
        if flow is not None:
            request.flow = flow.name
        response = self._stub.RegisterFeatureSet(request)
        self._reload_project()
        return FeatureSet(self._stub, self._rest_stub, response.feature_set)

    def get(self, feature_set_name, version=None):
        """Obtain an existing feature set.

        Args:
            feature_set_name: (str) A feature set name.
            version: (str) A specific version of feature set with format as "major.minor".

        Returns:
            FeatureSet: An existing feature set.

        Typical example:
            fs = project.feature_sets.get("feature_set_name", version=None)

        Raises:
            Exception: Version parameter must be in a format "major.minor".

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#obtaining-a-feature-set
        """
        request = pb.GetFeatureSetRequest()
        request.project_id = self._project.id
        request.feature_set_name = feature_set_name
        if version is not None:
            if not re.search(r"^\d+\.\d+$", str(version)):
                raise Exception('Version parameter must be in a format "major.minor".')
            request.version = str(version)
        response = self._stub.GetFeatureSet(request)
        return FeatureSet(self._stub, self._rest_stub, response.feature_set)

    def get_major_version(self, feature_set_name: str, major_version: int):
        """Obtain an existing last minor version of feature set for given major_version.

        Args:
            feature_set_name: (str) A feature set name.
            major_version: (int) A specific major version of feature set.

        Returns:
            FeatureSet: An existing feature set.

        Typical example:
            fs = project.feature_sets.get_major_version("feature_set_name", 2)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#obtaining-a-feature-set
        """
        request = pb.GetLastMinorFeatureSetForMajorInProjectRequest()
        request.project_id = self._project.id
        request.feature_set_name = feature_set_name
        request.feature_set_major_version = major_version
        response = self._stub.GetLastMinorFeatureSetForMajorInProject(request)
        return FeatureSet(self._stub, self._rest_stub, response.feature_set)

    def list(self, query: str = None, advanced_search_options: [AdvancedSearchOption] = None):
        """Return a generator which obtains the feature sets lazily.

        Args:
            query: (str) the name or description by which to search for the feature set
            advanced_search_options: (list(AdvancedSearchOption)) advanced search options
                to search by feature name, description or tag

        Returns:
            Iterable[FeatureSet]: A generator iterator object consists of feature sets.

        Typical example:
            advanced_search_options = [AdvancedSearchOption]
            project.feature_sets.list(advanced_search_options)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#listing-feature-sets-within-a-project
        """
        request = pb.FeatureSetSearchRequest()
        request.project_ids.extend([self._project.id])
        if query:
            request.query = query
        if advanced_search_options:
            request.options.extend([ad._to_proto() for ad in advanced_search_options])

        while request:
            response = self._stub.SearchFeatureSets(request)
            if response.next_page_token:
                request.page_token = response.next_page_token
            else:
                request = None
            for listable_feature_set in response.listable_feature_set:
                yield FeatureSet.from_listable_feature_set(self._stub, self._rest_stub, listable_feature_set)

    def __repr__(self):
        return Utils.pretty_print_proto(self._project)

    def _reload_project(self):
        request = pb.GetProjectRequest()
        request.project_name = self._project.name
        response = self._stub.GetProject(request)
        self._project = response.project
