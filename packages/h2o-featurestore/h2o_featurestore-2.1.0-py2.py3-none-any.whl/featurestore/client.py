import logging
import time

import grpc
from google.protobuf.empty_pb2 import Empty
from grpc import ChannelConnectivity

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
from ai.h2o.featurestore.api.v1 import CoreService_pb2_grpc

from .core import interactive_console
from .core.acl import AccessControlList
from .core.auth import AuthWrapper
from .core.browser import Browser
from .core.client_config import ClientConfig
from .core.collections.admin_projects import AdminProjects
from .core.collections.classifiers import Classifiers
from .core.collections.feature_set_reviews import FeatureSetReviews
from .core.collections.jobs import Jobs
from .core.collections.projects import Projects
from .core.config import ConfigUtils
from .core.credentials import CredentialsHelper
from .core.dashboard import Dashboard
from .core.data_source_wrappers import DataSourceWrapper
from .core.entities.component_versions import ComponentVersions
from .core.entities.extract_schema_job import ExtractSchemaJob
from .core.interceptors import AuthClientInterceptor, ExponentialBackoff, RetryOnRpcErrorClientInterceptor
from .core.schema import Schema
from .logger import LoggingConfiguration
from .rest_stub import RestStub


class Client:
    """Feature Store client."""

    def __init__(
        self, url: str, secure: bool = True, root_certificates: str = None, config: ClientConfig = ClientConfig()
    ):
        """Client constructor is used for initialization with following attributes.

        Args:
            url: (str) An endpoint address of the Feature Store server.
              (usually in ip:port format)
            secure: (bool) If True, turns on secure connection for Feature Store API.
              Default is False.
            root_certificates: (str) A file location of root certificates.
              Default is None.
            config: (ClientConfig) An additional client configuration.

        Typical usage example:

            config = ClientConfig(wait_for_backend=True, timeout=300)
            client = Client(url=<endpoint_url>, secure=False, root_certificates=None, config=config)

        For more details:
            https://docs.h2o.ai/featurestore/api/client_initialization.html
        """
        self.__init_internal(url.strip(), secure, root_certificates, config)

    def __init_internal(self, url: str, secure: bool, root_certificates: str, config: ClientConfig):
        self._client_config = config
        LoggingConfiguration.apply_config(config.log_level)
        options = [
            ("grpc.primary_user_agent", f"feature-store-py-cli/{self._get_client_version()}"),
        ]

        if secure:
            credentials = self._get_channel_credentials(root_certificates)
            channel = grpc.secure_channel(url, credentials, options)
        else:
            channel = grpc.insecure_channel(url, options)

        interceptors = [
            RetryOnRpcErrorClientInterceptor(
                max_attempts=5,
                sleeping_policy=ExponentialBackoff(init_backoff_ms=1000, max_backoff_ms=30000, multiplier=4),
                status_for_retry=[
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.DEADLINE_EXCEEDED,
                ],
            ),
            AuthClientInterceptor(self),
        ]
        self._channel = grpc.intercept_channel(channel, *interceptors)
        self._connection_state = None
        self._config = ConfigUtils.collect_properties()

        def on_connectivity_change(value):
            self._connection_state = value
            return

        self._channel.subscribe(on_connectivity_change, try_to_connect=True)
        if config.wait_for_backend:
            while self._connection_state != ChannelConnectivity.READY:
                logging.info(f"Connecting to the server {url} ...")
                time.sleep(2)
        else:
            logging.debug(f"Connecting to the server {url} ...")

        self._stub = CoreService_pb2_grpc.CoreServiceStub(self._channel)
        self.auth = AuthWrapper(self._stub)
        rest_stub = RestStub(self, root_certificates)
        admin_projects = AdminProjects(self._stub, rest_stub)
        self.projects = Projects(self._stub, rest_stub, admin_projects)
        self.jobs = Jobs(self._stub, rest_stub)
        self.classifiers = Classifiers(self._stub)
        self.acl = AccessControlList(self._stub, rest_stub)
        self.feature_set_reviews = FeatureSetReviews(self._stub, rest_stub)
        self.dashboard = Dashboard(self._stub, rest_stub)

        try:
            self._check_client_vs_server_version(self.get_version())
        except grpc.RpcError as error:
            logging.error(f"Connection to Feature Store API service '{url}' failed. Is the URL valid?")
            logging.debug(
                f"Received RPC error during client initialization: code={error.code()} message={error.details()}"
            )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._channel.close()
        return False

    def close(self):
        """Close the current working channel.

        It is good practice to close the connection after all action has proceeded.
        """
        self._channel.close()

    def get_version(self) -> ComponentVersions:
        """Return Feature Store component versions."""
        return ComponentVersions(self._get_client_version(), self._get_server_version())

    def _get_server_version(self) -> str:
        request = Empty()
        response = self._stub.GetVersion(request)
        return response.version

    @staticmethod
    def _get_client_version() -> str:
        from featurestore import __version__ as client_version

        return client_version

    def extract_schema_from_source_async(
        self, raw_data_location: DataSourceWrapper, credentials=None
    ) -> ExtractSchemaJob:
        """Create a schema extract job.

        This generates a new job for schema extraction from a provided data source.

        Args:
            raw_data_location: (CSVFile | CSVFolder | ParquetFile | ParquetFolder | JSONFile | JSONFolder |
              SnowflakeTable | SnowflakeCursor | JdbcTable | DeltaTable | MongoDbCollection | BigQueryTable)
              A source location of supported data source.
            credentials: (AzureKeyCredentials | AzureSasCredentials | AzurePrincipalCredentials | S3Credentials |
              SnowflakeCredentials | TeradataCredentials | PostgresCredentials | MongoDbCredentials| GcpCredentials)
              To access the provided data source. Default is None.

        Returns:
            ExtractSchemaJob: A job for schema extraction.

            A job is created with unique id and type ExtractSchema. For example:

            Job(id=<job_id>, type=ExtractSchema, done=False, childJobIds=[])

        For more details:
            Supported data sources:
              https://docs.h2o.ai/featurestore/supported_data_sources.html#supported-data-sources

            Passing credentials as parameters: An example
              https://docs.h2o.ai/featurestore/api/client_credentials.html#passing-credentials-as-a-parameters
        """
        request = pb.StartExtractSchemaJobRequest()
        data_source = raw_data_location.get_raw_data_location(self._stub)
        request.raw_data.CopyFrom(data_source)
        if not raw_data_location.is_local():
            CredentialsHelper.set_credentials(request, data_source, credentials)
        job_id = self._stub.StartExtractSchemaJob(request)
        return ExtractSchemaJob(self._stub, job_id)

    @interactive_console.record_stats
    def extract_schema_from_source(self, raw_data_location, credentials=None) -> Schema:
        """Extract a schema from a data source.

        Args:
            raw_data_location: (CSVFile | CSVFolder | ParquetFile | ParquetFolder | JSONFile | JSONFolder |
              SnowflakeTable | SnowflakeCursor | JdbcTable | DeltaTable | MongoDbCollection)
              A source location of supported data source.
            credentials: (AzureKeyCredentials | AzureSasCredentials | AzurePrincipalCredentials | S3Credentials |
              SnowflakeCredentials | TeradataCredentials | PostgresCredentials | MongoDbCredentials)
              To access the provided data source. Default is None.

        Returns:
            Schema: A schema with feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical usage example:

            credentials = S3Credentials(access_key, secret_key, region=None, endpoint=None, role_arn=None)
            source = CSVFile(path, delimiter=",")
            schema = Client(...).extract_schema_from_source(source, credentials)

        For more details:
            Supported data sources:
              https://docs.h2o.ai/featurestore/supported_data_sources.html#supported-data-sources

            Passing credentials as parameters: An example
              https://docs.h2o.ai/featurestore/api/client_credentials.html#passing-credentials-as-a-parameters
        """
        job = self.extract_schema_from_source_async(raw_data_location, credentials)
        return job.wait_for_result()

    @interactive_console.record_stats
    def extract_derived_schema(self, feature_sets, transformation) -> Schema:
        """Create a schema from an existing feature set using a selected transformation.

        Args:
            feature_sets: (list(str)) A list of existing feature sets.
            transformation: (Transformation) Represents an instance of Transformation.

        Returns:
            Schema: A schema with feature names and data types.

            For example:

            id INT, text STRING, label DOUBLE, state STRING, date TIMESTAMP

        Typical usage example:

            import featurestore.transformations as t
            spark_pipeline_transformation = t.SparkPipeline("...")
            schema = Client(...).extract_derived_schema([parent_feature_set], spark_pipeline_transformation)

        For more details:
            https://docs.h2o.ai/featurestore/api/schema_api.html#create-a-derived-schema-from-a-parent-feature-set-with-applied-transformation
        """
        job = self.extract_derived_schema_async(feature_sets, transformation)
        return job.wait_for_result()

    def extract_derived_schema_async(self, feature_sets, transformation) -> ExtractSchemaJob:
        """Create a schema extract job.

        This generates the new job for schema extraction from an existing feature set using
        selected transformation.

        Args:
            feature_sets: (list[str]) A list of existing feature sets.
            transformation: (Transformation) Represents an instance of Transformation.
              Find the supported transformations in more details section.

        Returns:
            ExtractSchemaJob: A job for schema extraction.

            A job is created with unique id and type ExtractSchema. For example:

            Job(id=<job_id>, type=ExtractSchema, done=False, childJobIds=[])

        For more details:
            Supported derived transformation:
              https://docs.h2o.ai/featurestore/supported_derived_transformation.html#supported-derived-transformation
        """
        transformation._initialize(self._stub)
        request = pb.StartExtractSchemaJobRequest(
            derived_from=pb.DerivedInformation(
                feature_set_ids=[pb.VersionedId(id=f.id, major_version=f.major_version) for f in feature_sets],
                transformation=transformation._to_proto(),
            )
        )

        job_id = self._stub.StartExtractSchemaJob(request)
        return ExtractSchemaJob(self._stub, job_id)

    def _has_online_retrieve_permissions(self, project_name, feature_set_name):
        request = pb.HasPermissionToRetrieveRequest()
        request.project_name = project_name
        request.feature_set_name = feature_set_name
        response = self._stub.HasPermissionToRetrieve(request)
        return response.has_retrieve_permission

    def show_progress(self, interactive):
        """Enable or disable interactive logging. Logging is enabled by default.

        Args:
            interactive: (bool) If True, enables interactive logging.

        Typical usage example:
            client.show_progress(False)
        """
        ConfigUtils.set_property(self._config, ConfigUtils.INTERACTIVE_LOGGING, str(interactive))

    @staticmethod
    def _get_channel_credentials(cert_location: str) -> grpc.ChannelCredentials:
        if cert_location is not None:
            with open(cert_location, "rb") as cert_file:
                return grpc.ssl_channel_credentials(cert_file.read())
        return grpc.ssl_channel_credentials()

    @staticmethod
    def _check_client_vs_server_version(component_versions):
        logging.info(f"Server version: {component_versions.server_version}")
        logging.info(f"Client version: {component_versions.client_version}")

        if component_versions.client_is_newer_than_server():
            logging.warning(
                """\
The client version ({0}) is newer then server version ({1}).
It's recommended to downgrade the client. Otherwise, an UNIMPLEMENTED exception will be thrown in case
that a new method (not supported by server) were utilized.""".format(
                    component_versions.client_version, component_versions.server_version
                )
            )
        elif component_versions.server_is_newer_than_client():
            logging.warning(
                """\
The client version ({0}) is older then server version ({1}).
It's recommended to upgrade the client.""".format(
                    component_versions.client_version, component_versions.server_version
                )
            )

    def open_website(self):
        """This opens the Feature Store Web UI.

        This opens the returned URL in the browser (if it's not possible to open the browser, you will
        have to do this manually).

        For more details:
            https://docs.h2o.ai/featurestore/api/client_initialization
        """
        Browser(self._stub).open_website()
