from typing import Iterator

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from featurestore.core.entities.feature_set_review import FeatureSetReviewRequest, FeatureSetUserReview


class FeatureSetReviews:
    def __init__(self, stub, rest_stub, project_id=None):
        self._stub = stub
        self._rest_stub = rest_stub
        self._project_id = project_id

    def manageable_requests(self, filters=None) -> Iterator[FeatureSetReviewRequest]:
        """List pending manageable feature set review requests.

        Args:
            (ReviewStatuses) Object represents a specific review status.
            filters: (list[ReviewStatuses]) Filter includes the status of review
            (either IN_PROGRESS, APPROVED or REJECTED).

        Returns:
            Generator of feature set review requests

        Typical example:
            filters = [ReviewStatuses.IN_PROGRESS]
            reviews = client.feature_set_reviews.manageable_requests()

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-review-requests-from-other-users
        """
        request = pb.ListFeatureSetsToReviewRequest(filters=filters, project_id=self._project_id)
        return (
            FeatureSetReviewRequest(self._stub, self._rest_stub, entry)
            for entry in self.__paged_response_to_request(request, self._stub.ListFeatureSetsToReview)
        )

    def my_requests(self, filters=None) -> Iterator[FeatureSetUserReview]:
        """List existing feature set review requests belonging to the user.

        Args:
            (ReviewStatuses) Object represents a specific review status.
            filters: (list[ReviewStatuses]) Filter includes the status of review
            (either IN_PROGRESS, APPROVED or REJECTED).

        Returns:
            Generator of feature set user review requests

        Typical example:
            filters = [ReviewStatuses.IN_PROGRESS]
            reviews = client.feature_set_reviews.my_requests(filters)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-own-feature-sets-in-review
        """
        request = pb.ListFeatureSetReviewsPageRequest(filters=filters, project_id=self._project_id)
        return (
            FeatureSetUserReview(self._stub, self._rest_stub, entry)
            for entry in self.__paged_response_to_request(request, self._stub.ListFeatureSetsReviewsPage)
        )

    def __paged_response_to_request(self, request, call):
        while request:
            response = call(request)
            if response.next_page_token:
                request.page_token = response.next_page_token
            else:
                request = None
            for entry in response.entries:
                yield entry
