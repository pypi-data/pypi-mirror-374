import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
import ai.h2o.featurestore.api.v1.FeatureSetProtoApi_pb2 as FeatureSetApi

from ..schema import FeatureSchema, FeatureSchemaMonitoring, FeatureSchemaSpecialData, Schema


class FeatureSetSchema:
    def __init__(self, stub, feature_set):
        self._feature_set = feature_set
        self._stub = stub

    def get(self):
        """Get a schema of a feature set.

        Returns:
            Schema: A schema with feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical example:
            fs.schema.get()
        """
        return Schema.create_from(self._feature_set)

    def is_compatible_with(self, new_schema, compare_data_types=True):
        """Compare a schema of a feature set with a schema of new data source.

        Args:
            new_schema: (Schema) A new schema to check compatibility with.
            compare_data_types: (bool) Object indicates whether data type needs to be compared or not.

        Returns:
            bool: A boolean describes whether compatible or not.

        Typical example:
            fs.schema.is_compatible_with(new_schema, compare_data_types=True)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#checking-schema-compatibility
        """
        request = pb.FeatureSetSchemaCompatibilityRequest()
        request.original_schema.extend(self.get()._to_proto_schema())
        request.new_schema.extend(new_schema._to_proto_schema())
        request.compare_data_types = compare_data_types
        response = self._stub.IsFeatureSetSchemaCompatible(request)
        return response.is_compatible

    def patch_from(self, new_schema, compare_data_types=True):
        """Patch a new schema with a schema of a feature set.

        Patch schema checks for matching features between the ‘new schema’ and the existing ‘fs.schema’.
        If there is a match, then the metadata such as special_data, description, etc are copied into the new_schema.

        Args:
            new_schema: (Schema) A new schema that needs to be patched.
            compare_data_types: (bool) Object indicates whether data type are to be compared while patching.

        Returns:
            Schema: A new schema after patches.

        Typical example:
            fs.schema.patch_from(new_schema, compare_data_types=True)

        For more details:
            https://docs.h2o.ai/featurestore/api/feature_set_api.html#patching-new-schema
        """
        request = pb.FeatureSetSchemaPatchRequest()
        request.original_schema.extend(self.get()._to_proto_schema())
        request.new_schema.extend(new_schema._to_proto_schema())
        request.compare_data_types = compare_data_types
        response = self._stub.FeatureSetSchemaPatch(request)
        return Schema(self._create_schema_from_proto(response.schema), True)

    @staticmethod
    def _create_schema_from_proto(schema):
        return [
            FeatureSchema(
                feature_schema.name,
                feature_schema.data_type,
                nested_features_schema=FeatureSetSchema._create_schema_from_proto(feature_schema.nested),
                special_data=FeatureSchemaSpecialData(
                    spi=feature_schema.special_data.spi,
                    pci=feature_schema.special_data.pci,
                    rpi=feature_schema.special_data.rpi,
                    demographic=feature_schema.special_data.demographic,
                    sensitive=feature_schema.special_data.sensitive,
                ),
                _feature_type=FeatureSetApi.FeatureType.Name(feature_schema.feature_type),
                description=feature_schema.description,
                classifiers=set(feature_schema.classifiers),
                custom_data=feature_schema.custom_data,
                monitoring=FeatureSchemaMonitoring(anomaly_detection=feature_schema.monitoring.anomaly_detection),
            )
            for feature_schema in schema
        ]
