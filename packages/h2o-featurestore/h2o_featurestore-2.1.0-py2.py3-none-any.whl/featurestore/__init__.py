from codecs import open
from os import path

from featurestore.client import Client
from featurestore.core.access_modifier import AccessModifier
from featurestore.core.client_config import ClientConfig
from featurestore.core.collections.classifiers import EmptyClassifier, RegexClassifier, SampleClassifier
from featurestore.core.data_source_wrappers import (
    BigQueryTable,
    CSVFile,
    CSVFolder,
    DeltaTable,
    DeltaTableFilter,
    JdbcTable,
    JSONFile,
    JSONFolder,
    MongoDbCollection,
    ParquetFile,
    ParquetFolder,
    PartitionOptions,
    Proxy,
    SnowflakeCursor,
    SnowflakeTable,
    SparkDataFrame,
)
from featurestore.core.entities.advanced_search_option import AdvancedSearchOption
from featurestore.core.entities.backfill_option import BackfillOption
from featurestore.core.feature_set_flow import FeatureSetFlow
from featurestore.core.schema import FeatureSchema, Schema
from featurestore.core.storage_optimization import CompactOptimization, ZOrderByOptimization
from featurestore.core.transformations import DriverlessAIMOJO, JoinFeatureSets, JoinFeatureSetsType, SparkPipeline
from featurestore.core.user_credentials import (
    AzureKeyCredentials,
    AzurePrincipalCredentials,
    AzureSasCredentials,
    GcpCredentials,
    MongoDbCredentials,
    PostgresCredentials,
    S3Credentials,
    SnowflakeCredentials,
    SnowflakeKeyPairCredentials,
    TeradataCredentials,
)


def __get_version():
    here = path.abspath(path.dirname(__file__))
    with open(path.join(here, "version.txt"), encoding="utf-8") as f:
        return f.read().strip()


__version__ = __get_version()
__all__ = [
    "Client",
    "FeatureSchema",
    "Schema",
    "CSVFile",
    "CSVFolder",
    "JSONFile",
    "JSONFolder",
    "MongoDbCollection",
    "ParquetFile",
    "ParquetFolder",
    "SnowflakeTable",
    "JdbcTable",
    "PartitionOptions",
    "SnowflakeCursor",
    "DeltaTable",
    "DeltaTableFilter",
    "Proxy",
    "JSONFolder",
    "Schema",
    "SparkDataFrame",
    "ClientConfig",
    "AzureKeyCredentials",
    "AzureSasCredentials",
    "AzurePrincipalCredentials",
    "S3Credentials",
    "TeradataCredentials",
    "SnowflakeCredentials",
    "SnowflakeKeyPairCredentials",
    "PostgresCredentials",
    "MongoDbCredentials",
    "SparkPipeline",
    "DriverlessAIMOJO",
    "JoinFeatureSetsType",
    "JoinFeatureSets",
    "EmptyClassifier",
    "RegexClassifier",
    "SampleClassifier",
    "BackfillOption",
    "FeatureSetFlow",
    "AdvancedSearchOption",
    "CompactOptimization",
    "ZOrderByOptimization",
    "GcpCredentials",
    "BigQueryTable",
    "AccessModifier",
]
