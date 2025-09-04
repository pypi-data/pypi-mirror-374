import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..utils import Utils
from .feature_set import FeatureSet
from .user import User


class FeatureSetReview:
    def __init__(self, stub, rest_stub, review):
        self._stub = stub
        self._rest_stub = rest_stub
        self._review = review

    @property
    def review_id(self):
        return self._review.review_id

    @property
    def project_name(self):
        return self._review.project_name

    @property
    def feature_set_name(self):
        return self._review.feature_set_name

    @property
    def feature_set_major_version(self):
        return self._review.feature_set_major_version

    @property
    def feature_set_id(self):
        return self._review.feature_set_id

    @property
    def created_at(self):
        return Utils.timestamp_to_string(self._review.created_at)

    @property
    def status(self):
        return pb.ReviewStatus.Name(self._review.status)

    def __repr__(self):
        return Utils.pretty_print_proto(self._review)


class FeatureSetReviewRequest(FeatureSetReview):
    @property
    def author(self):
        return User(self._review.owner)

    def approve(self, reason):
        """Approve a review request.

        Args:
        reason: (str) A reason for review request approval.

        Typical example:
        review_request.approve("it will be fun")

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-review-requests-from-other-users
        """
        request = pb.ApproveReviewRequest(review_id=self._review.review_id, reason=reason)
        self._stub.ApproveReview(request)

    def reject(self, reason):
        """Reject a review request.

        Args:
        reason: (str) A reason for review request rejection.

        Typical example:
        review_request.reject("it's not ready yet")

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-review-requests-from-other-users
        """
        request = pb.RejectReviewRequest(review_id=self._review.review_id, reason=reason)
        self._stub.RejectReview(request)

    def get_feature_set(self) -> FeatureSet:
        """Get a feature set to review.

        Returns:
            A corresponding feature set.

        Typical example:
            review_request.get_feature_set()
        """
        request = pb.GetFeatureSetToReviewRequest(review_id=self._review.review_id)
        response = self._stub.GetFeatureSetToReview(request)
        return FeatureSet(self._stub, self._rest_stub, response.feature_set)

    def get_preview(self):
        """Preview the data of feature set to review.

        This previews up to a maximum of 100 rows and 50 features.

        Returns:
            list[dict]: A list of dictionary which contains JSON rows.

        Typical example:
            review_request.get_preview()
        """
        request = pb.GetFeatureSetPreviewToReviewRequest(
            review_id=self._review.review_id,
        )
        response = self._stub.GetFeatureSetPreviewToReview(request)
        if response.preview_url:
            json_response = Utils.fetch_preview_as_json_array(response.preview_url)
            return json_response
        else:
            return []


class FeatureSetUserReview(FeatureSetReview):
    @property
    def reviewer(self):
        return User(self._review.reviewer)

    @property
    def reviewed_at(self):
        return Utils.timestamp_to_string(self._review.reviewed_at)

    @property
    def reason(self):
        return self._review.reason

    def get_feature_set(self) -> FeatureSet:
        """Get a feature set in review.

        Returns:
            A corresponding feature set.

        Typical example:
            review_request.get_feature_set()

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-own-feature-sets-in-review
        """
        request = pb.GetFeatureSetInReviewRequest(review_id=self._review.review_id)
        response = self._stub.GetFeatureSetInReview(request)
        return FeatureSet(self._stub, self._rest_stub, response.feature_set)

    def get_preview(self):
        """Preview the data of feature set in review.

        This previews up to a maximum of 100 rows and 50 features.

        Returns:
            list[dict]: A list of dictionary which contains JSON rows.

        Typical example:
            review_request.get_preview()

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-own-feature-sets-in-review
        """
        request = pb.GetFeatureSetPreviewInReviewRequest(
            review_id=self._review.review_id,
        )
        response = self._stub.GetFeatureSetPreviewInReview(request)
        if response.preview_url:
            json_response = Utils.fetch_preview_as_json_array(response.preview_url)
            return json_response
        else:
            return []

    def delete(self):
        """Delete the currently major version in review.

        Review must be in status IN_PROGRESS or REJECTED.

        Typical example:
            review_request.delete()

        For more details:
        https://docs.h2o.ai/featurestore/api/feature_set_review_api#manage-own-feature-sets-in-review
        """
        request = pb.DeleteRejectedFeatureSetRequest(review_id=self._review.review_id)
        self._stub.DeleteFeatureSetVersionInReview(request)
