from typing import Iterator

from google.protobuf.empty_pb2 import Empty

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from featurestore.core.entities.feature_set_popularity import FeatureSetPopularity
from featurestore.core.entities.pinned_feature_set import PinnedFeatureSet
from featurestore.core.entities.recently_used_feature_set import RecentlyUsedFeatureSet
from featurestore.core.entities.recently_used_project import RecentlyUsedProject


class Dashboard:
    def __init__(self, stub, rest_stub):
        self._stub = stub
        self._rest_stub = rest_stub

    def get_feature_sets_popularity(self):
        """Get popular feature sets.

        Returns:
            List of feature sets popularity

        Typical example:
            fs_popularity = client.dashboard.get_feature_sets_popularity()
        """
        response = self._stub.GetFeatureSetsPopularity(Empty())
        return [
            FeatureSetPopularity(self._stub, self._rest_stub, popular_feature_set)
            for popular_feature_set in response.feature_sets
        ]

    def get_recently_used_projects(self):
        """Get projects that were recently utilized.

        Returns:
            List of references to projects

        Typical example:
            recently_used_projects = client.dashboard.get_recently_used_projects()
        """
        response = self._stub.GetRecentlyUsedProjects(Empty())
        return [RecentlyUsedProject(self._stub, self._rest_stub, project) for project in response.projects]

    def get_recently_used_feature_sets(self):
        """Get feature sets that were recently utilized.

        Returns:
            List of references to feature sets

        Typical example:
            recently_used_feature_sets = client.dashboard.get_recently_used_feature_sets()
        """
        response = self._stub.GetRecentlyUsedFeatureSets(Empty())
        return [
            RecentlyUsedFeatureSet(self._stub, self._rest_stub, feature_set) for feature_set in response.feature_sets
        ]

    def list_pinned_feature_sets(self) -> Iterator[PinnedFeatureSet]:
        """List feature sets that were pinned by current user.

        Returns:
            Iterator[PinnedFeatureSet]: An iterator which obtains the pinned feature sets lazily.

        Typical example:
            client.dashboard.list_pinned_feature_sets()
        """
        request = pb.PinnedFeatureSetsRequest()
        while request:
            response = self._stub.ListPinnedFeatureSets(request)
            if response.next_page_token:
                request.page_token = response.next_page_token
            else:
                request = None
            for feature_set in response.feature_sets:
                yield PinnedFeatureSet(self._stub, self._rest_stub, feature_set)
