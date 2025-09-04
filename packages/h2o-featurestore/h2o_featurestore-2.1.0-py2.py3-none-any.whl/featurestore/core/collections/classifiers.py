from abc import ABC, abstractmethod

from google.protobuf.empty_pb2 import Empty

import ai.h2o.featurestore.api.v1.RecommendationProtoApi_pb2 as pb


class Classifier(ABC):
    @abstractmethod
    def _to_proto(self):
        raise NotImplementedError("Method `__to_proto` needs to be implemented by the child class")

    @staticmethod
    def _from_proto(classifier: pb.RecommendationClassifier):
        oneof_kind = classifier.WhichOneof("matching_policy")
        if oneof_kind == "regex":
            return RegexClassifier(
                classifier.name,
                classifier.regex.regex,
                classifier.regex.percentage_match,
            )
        elif oneof_kind == "sample":
            return SampleClassifier(
                classifier.name,
                classifier.sample.feature_set_id,
                classifier.sample.feature_set_major_version,
                classifier.sample.column_name,
                classifier.sample.sample_fraction,
                classifier.sample.fuzzy_distance,
                classifier.sample.percentage_match,
            )
        elif oneof_kind is None:
            return EmptyClassifier(classifier.name)
        else:
            raise ValueError("Not supported classifier provided")


class EmptyClassifier(Classifier):
    def __init__(self, name):
        self.name = name

    def _to_proto(self):
        return pb.RecommendationClassifier(name=self.name)

    def __repr__(self):
        return f"EmptyClassifier(name={self.name})"


class RegexClassifier(Classifier):
    def __init__(self, name, regex, percentage_match):
        self.name = name
        self.regex = regex
        self.percentage_match = percentage_match

    def _to_proto(self):
        return pb.RecommendationClassifier(
            name=self.name,
            regex=pb.RecommendationRegexMatchingPolicy(regex=self.regex, percentage_match=self.percentage_match),
        )

    def __repr__(self):
        return f"RegexClassifier(name={self.name}, regex={self.regex}, percentage_match={self.percentage_match})"


class SampleClassifier(Classifier):
    def __init__(
        self,
        name: str,
        feature_set_id: str,
        feature_set_major_version: int,
        column_name: str,
        sample_fraction: float,
        fuzzy_distance: int,
        percentage_match: int,
    ):
        self.name = name
        self.feature_set_id = feature_set_id
        self.feature_set_major_version = feature_set_major_version
        self.column_name = column_name
        self.sample_fraction = sample_fraction
        self.fuzzy_distance = fuzzy_distance
        self.percentage_match = percentage_match

    @classmethod
    def from_feature_set(
        cls,
        feature_set,
        name,
        column_name,
        sample_fraction,
        fuzzy_distance,
        percentage_match,
    ):
        return cls(
            name,
            feature_set.id,
            feature_set.major_version,
            column_name,
            sample_fraction,
            fuzzy_distance,
            percentage_match,
        )

    def _to_proto(self):
        return pb.RecommendationClassifier(
            name=self.name,
            sample=pb.RecommendationSampleMatchingPolicy(
                feature_set_id=self.feature_set_id,
                feature_set_major_version=self.feature_set_major_version,
                column_name=self.column_name,
                sample_fraction=self.sample_fraction,
                fuzzy_distance=self.fuzzy_distance,
                percentage_match=self.percentage_match,
            ),
        )

    def __repr__(self):
        return (
            f"SampleClassifier(name={self.name}, "
            f"feature_set_id={self.feature_set_id}, "
            f"feature_set_major_version={self.feature_set_major_version}, "
            f"column_name={self.column_name}, "
            f"sample_fraction={self.sample_fraction}, "
            f"fuzzy_distance={self.fuzzy_distance}, "
            f"percentage_match={self.percentage_match})"
        )


class Classifiers:
    def __init__(self, stub):
        self._stub = stub

    def list(self) -> [Classifier]:
        """Return all configured classifiers on the backend.

        Returns:
            list[Classifier]: A list of Classifier - EmptyClassifier | RegexClassifier | SampleClassifier.

            For example:

            [RegexClassifier(name=FS_TEST_CLASSIFIER, regex=auto_apply_classifier, percentage_match=100)]

        Typical example:
            client.classifiers.list()

        """
        request = Empty()
        response = self._stub.ListRecommendationClassifiers(request)
        return [Classifier._from_proto(classifier) for classifier in response.classifiers]

    def create(self, classifier) -> None:
        """Register a new classifier.

        Feature Store administrators can register new classifiers in the system.

        Args:
            classifier: (str | Classifier) Object represents String or Classifier.

        Typical example:
            client.classifiers.create("classifierName")
            client.classifiers.create(RegexClassifier("classifierName", "test", 10))

        Raises:
            ValueError: Parameter classifier should be string or object of Classifier class.

        For more details:
            https://docs.h2o.ai/featurestore/api/recommendation_api.html#creating-a-new-classifier
        """
        if isinstance(classifier, str):
            classifier_to_send = EmptyClassifier(classifier)
        elif isinstance(classifier, Classifier):
            classifier_to_send = classifier
        else:
            raise ValueError("Parameter classifier should be string or object of Classifier class")

        request = pb.CreateRecommendationClassifierRequest(classifier=classifier_to_send._to_proto())
        self._stub.CreateRecommendationClassifier(request)

    def update(self, classifier: Classifier):
        """Update an existing classifier.

        Feature Store administrators can update the classifiers.

        Args:
            classifier: (Classifier) Object represents Classifier.
              EmptyClassifier | RegexClassifier | SampleClassifier

        Typical example:
            client.classifiers.update(RegexClassifier("classifierName", "test", 10))

        For more details:
            https://docs.h2o.ai/featurestore/api/recommendation_api.html#updating-an-existing-classifier
        """
        request = pb.UpdateRecommendationClassifierRequest(classifier=classifier._to_proto())
        self._stub.UpdateRecommendationClassifier(request)

    def delete(self, name: str):
        """Delete an existing classifier.

        Feature Store administrators can delete the classifiers.

        Args:
            name: (str) A name of an existing classifier.

        Typical example:
            client.classifiers.delete("classifierName")

        For more details:
            https://docs.h2o.ai/featurestore/api/recommendation_api.html#deleting-an-existing-classifier
        """
        request = pb.DeleteRecommendationClassifierRequest(classifier_name=name)
        self._stub.DeleteRecommendationClassifier(request)

    def __repr__(self):
        return "Recommendation classifiers"
