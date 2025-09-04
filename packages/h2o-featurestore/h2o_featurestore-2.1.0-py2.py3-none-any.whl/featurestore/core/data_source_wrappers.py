import os
import re
import tempfile
from abc import ABC, abstractmethod

import requests

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb
import ai.h2o.featurestore.api.v1.FeatureSetSearch_pb2 as pb_search
from ai.h2o.featurestore.api.v1.CoreService_pb2_grpc import CoreServiceStub
from ai.h2o.featurestore.api.v1.FeatureSetSearch_pb2 import BooleanFilter, NumericalFilter, TextualFilter

from .commons.spark_utils import SparkUtils
from .utils import Utils


class DataSourceWrapper(ABC):
    def is_local(self):
        return False

    def _write_to_storage(self, stub: CoreServiceStub, filter_pattern=""):
        pass

    @abstractmethod
    def get_raw_data_location(self, stub: CoreServiceStub):
        raise Exception("Not implemented")


class FileDataSourceWrapper(DataSourceWrapper, ABC):
    def __init__(self, path: str):
        self.path: str = path
        self._remote_path = None

    def is_local_file(self):
        if self.is_local():
            local_path = self.path.removeprefix("file://")
            return os.path.isfile(local_path)
        else:
            return False

    def is_local_directory(self):
        if self.is_local():
            local_path = self.path.removeprefix("file://")
            return os.path.isdir(local_path)
        else:
            return False

    def is_local(self):
        return self.path.lower().startswith("file://")

    def _write_to_storage(self, stub: CoreServiceStub, filter_pattern=""):
        if self._remote_path:
            return
        if not self.is_local():
            raise ValueError("Only local file can be written to temp storage")

        local_path = self.path.removeprefix("file://")
        if not os.path.exists(local_path):
            raise ValueError(f"Path {local_path} does not exist")
        files_with_md5_checksum = {}
        if self.is_local_file():
            if os.path.getsize(local_path) > 0:
                md5_checksum = Utils.generate_md5_checksum(local_path)
                files_with_md5_checksum = {os.path.basename(local_path): md5_checksum}
        elif not filter_pattern:
            for file in os.listdir(local_path):
                if os.path.getsize(os.path.join(local_path, file)) > 0:
                    md5_checksum = Utils.generate_md5_checksum(os.path.join(local_path, file))
                    files_with_md5_checksum[file] = md5_checksum
        else:
            segments = filter_pattern.rsplit("/", 1)
            file_pattern = re.compile(segments[1]) if len(segments) > 1 else re.compile(filter_pattern)
            path_pattern = re.compile(segments[0] + "$") if len(segments) > 1 else re.compile(".*")
            for dirpath, dirnames, filenames in os.walk(local_path):
                for fn in filenames:
                    if file_pattern.match(fn) and path_pattern.search(dirpath):
                        file_path = os.path.join(dirpath, fn)
                        rel_file_path = os.path.relpath(file_path, local_path)
                        md5_checksum = Utils.generate_md5_checksum(file_path)
                        files_with_md5_checksum[rel_file_path] = md5_checksum

        if not files_with_md5_checksum:
            if self.is_local_file():
                raise ValueError(f"File {local_path} is empty")
            else:
                raise ValueError(f"Directory {local_path} is empty")

        request = pb.GenerateTemporaryUploadRequest(files_with_md5_checksum=files_with_md5_checksum)
        write_info: pb.GenerateTemporaryUploadResponse = stub.GenerateTemporaryUpload(request)
        for file, md5_checksum in files_with_md5_checksum.items():
            if self.is_local_file():
                absolute_path = local_path
            else:
                absolute_path = os.path.join(local_path, file)
            with open(absolute_path, "rb") as local_file:
                response = requests.put(
                    url=write_info.file_responses[file].presign_url,
                    data=local_file,
                    headers=write_info.file_responses[file].headers,
                )
                if response.status_code not in range(200, 300):
                    raise Exception(
                        f"File upload {file} failed with status code {response.status_code} "
                        f"and message"
                        f" {response.text}"
                    )
        if self.is_local_file():
            self._remote_path = write_info.file_responses[os.path.basename(local_path)].url
        else:
            self._remote_path = write_info.directory_url

    @property
    def external_path(self):
        if self._remote_path:
            return self._remote_path
        else:
            return self.path


class DeltaTableFilter:
    def __init__(self, column, operator, value):
        self.column = column
        self.operator = operator
        self.value = value
        self._filter = self.__build()

    def __build(self):
        if isinstance(self.value, str):
            return pb_search.Filter(text=TextualFilter(field=self.column, operator=self.operator, value=[self.value]))
        elif isinstance(self.value, (int, float)):
            return pb_search.Filter(
                numeric=NumericalFilter(field=self.column, operator=self.operator, value=self.value)
            )
        elif isinstance(self.value, bool):
            return pb_search.Filter(boolean=BooleanFilter(field=self.column, operator=self.operator, value=self.value))


class SparkDataFrame(DataSourceWrapper):
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self._write_path = None

    def is_local(self):
        return True

    def _write_to_storage(self, stub):
        if self._write_path:
            return

        from pyspark.sql import SparkSession  # Local import

        spark = SparkSession.builder.getOrCreate()

        SparkUtils.configure_user_spark(spark)
        spark.conf.set("spark.sql.session.timeZone", "UTC")
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = os.path.join(tmp, "dt")
            self.dataframe.write.parquet(output_dir)
            parquet_files = [file for file in os.listdir(output_dir) if file.endswith(".parquet")]
            files_with_md5_checksum = {}
            for file in parquet_files:
                md5_checksum = Utils.generate_md5_checksum(os.path.join(output_dir, file))
                files_with_md5_checksum[file] = md5_checksum

            request = pb.GenerateTemporaryUploadRequest(files_with_md5_checksum=files_with_md5_checksum)
            write_info: pb.GenerateTemporaryUploadResponse = stub.GenerateTemporaryUpload(request)
            for file, md5_checksum in files_with_md5_checksum.items():
                with open(os.path.join(output_dir, file), "rb") as local_file:
                    response = requests.put(
                        url=write_info.file_responses[file].presign_url,
                        data=local_file,
                        headers=write_info.file_responses[file].headers,
                    )
                    if response.status_code not in range(200, 300):
                        raise Exception(
                            f"File upload {file} failed with status code {response.status_code} "
                            f"and message"
                            f" {response.text}"
                        )

            self._write_path = write_info.directory_url

    def get_raw_data_location(self, stub: CoreServiceStub):
        if not self._write_path:
            self._write_to_storage(stub)
        parquet = pb.ParquetFileSpec()
        parquet.path = self._write_path
        raw_data_location = pb.RawDataLocation()
        raw_data_location.parquet.CopyFrom(parquet)
        return raw_data_location


class CSVFile(FileDataSourceWrapper):
    def get_raw_data_location(self, stub: CoreServiceStub):
        if self.is_local():
            self._write_to_storage(stub)
        raw_data_location = pb.RawDataLocation()
        csv = pb.CSVFileSpec()
        csv.path = self.external_path
        csv.delimiter = self.delimiter
        raw_data_location.csv.CopyFrom(csv)
        return raw_data_location

    def __init__(self, path, delimiter=","):
        super().__init__(path)
        self.delimiter = delimiter


class JSONFile(FileDataSourceWrapper):
    def __init__(self, path, multiline=False):
        super().__init__(path)
        self.multiline = multiline

    def get_raw_data_location(self, stub: CoreServiceStub):
        if self.is_local():
            self._write_to_storage(stub)
        raw_data_location = pb.RawDataLocation()
        json = pb.JSONFileSpec()
        json.path = self.external_path
        json.multiline = self.multiline
        raw_data_location.json.CopyFrom(json)
        return raw_data_location


class ParquetFile(FileDataSourceWrapper):
    def __init__(self, path):
        super().__init__(path)

    def get_raw_data_location(self, stub: CoreServiceStub):
        if self.is_local():
            self._write_to_storage(stub)
        raw_data_location = pb.RawDataLocation()
        parquet = pb.ParquetFileSpec()
        parquet.path = self.external_path
        raw_data_location.parquet.CopyFrom(parquet)
        return raw_data_location


class Proxy:
    def __init__(self, host="", port=0, user="", password=""):
        if port and not host:
            raise ValueError("Proxy port specified but host is missing!")
        if not port and host:
            raise ValueError("Proxy host specified but port is missing!")
        if port and host:
            if user and not password:
                raise ValueError("Proxy user specified but password is missing!")
            if not user and password:
                raise ValueError("Proxy password specified but user is missing!")
        self.host = host
        self.port = port
        self.user = user
        self.password = password


class SnowflakeTable(DataSourceWrapper):
    def __init__(
        self,
        url,
        warehouse,
        database,
        schema,
        table="",
        query="",
        insecure=False,
        proxy=None,
        role="",
        account="",
    ):
        if not (query or table):
            raise ValueError("table or query is required!")
        if query and table:
            raise ValueError("Only one of table or query is supported!")

        self.table = table
        self.database = database
        self.url = url
        self.query = query
        self.warehouse = warehouse
        self.schema = schema
        self.insecure = insecure
        self.proxy = proxy
        self.role = role
        self.account = account

    def get_raw_data_location(self, stub: CoreServiceStub):
        raw_data_location = pb.RawDataLocation()
        snowflake = pb.SnowflakeTableSpec()
        snowflake.table = self.table
        snowflake.database = self.database
        snowflake.url = self.url
        snowflake.warehouse = self.warehouse
        snowflake.schema = self.schema
        snowflake.query = self.query
        snowflake.insecure = self.insecure
        snowflake.role = self.role
        snowflake.account = self.account
        if self.proxy:
            snowflake.proxy.host = self.proxy.host
            snowflake.proxy.port = self.proxy.port
            snowflake.proxy.user = self.proxy.user
            snowflake.proxy.password = self.proxy.password
        raw_data_location.snowflake.CopyFrom(snowflake)
        return raw_data_location


class JdbcTable(DataSourceWrapper):
    def __init__(
        self,
        connection_url,
        table="",
        query="",
        partition_options=None,
    ):
        if not (table or query):
            raise ValueError("Table or query is required!")
        if table and query:
            raise ValueError("Only one of table or query is supported!")
        self.table = table
        self.query = query
        self.connection_url = connection_url
        self.partition_options = partition_options

    def get_raw_data_location(self, stub: CoreServiceStub):
        raw_data_location = pb.RawDataLocation()
        jdbc = pb.JDBCTableSpec()
        jdbc.table = self.table
        jdbc.connection_url = self.connection_url
        jdbc.query = self.query
        if self.partition_options is not None:
            jdbc.num_partitions = self.partition_options.num_partitions
            jdbc.partition_column = self.partition_options.partition_column
            jdbc.lower_bound = self.partition_options.lower_bound
            jdbc.upper_bound = self.partition_options.upper_bound
            jdbc.fetch_size = self.partition_options.fetch_size
        raw_data_location.jdbc.CopyFrom(jdbc)
        return raw_data_location


class PartitionOptions:
    def __init__(
        self,
        num_partitions=None,
        partition_column=None,
        lower_bound=None,
        upper_bound=None,
        fetch_size=1000,
    ):
        self.num_partitions = num_partitions
        self.partition_column = partition_column
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.fetch_size = fetch_size


class SnowflakeCursor(DataSourceWrapper):
    def __init__(
        self,
        url,
        warehouse,
        database,
        schema,
        cursor,
        insecure=False,
        proxy=None,
        role="",
        account="",
    ):
        self.cursor = cursor
        self.database = database
        self.url = url
        self.warehouse = warehouse
        self.schema = schema
        self.insecure = insecure
        self.proxy = proxy
        self.role = role
        self.account = account

    def get_raw_data_location(self, stub: CoreServiceStub):
        raw_data_location = pb.RawDataLocation()
        snowflake = pb.SnowflakeTableSpec()
        snowflake.table = ""
        snowflake.database = self.database
        snowflake.url = self.url
        snowflake.warehouse = self.warehouse
        snowflake.schema = self.schema
        snowflake.query = self.get_latest_query()
        snowflake.insecure = self.insecure
        snowflake.role = self.role
        if self.proxy:
            snowflake.proxy.host = self.proxy.host
            snowflake.proxy.port = self.proxy.port
            snowflake.proxy.user = self.proxy.user
            snowflake.proxy.password = self.proxy.password
        raw_data_location.snowflake.CopyFrom(snowflake)
        return raw_data_location

    def get_latest_query(self):
        query = (
            "SELECT QUERY_TEXT::VARCHAR "
            "FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY_BY_SESSION(RESULT_LIMIT => 10)) "
            "WHERE QUERY_ID=%s"
        )
        self.cursor.execute(query, (self.cursor.sfqid,))  # get the last executed query using the query id
        try:
            latest_query = self.cursor.fetchone()[0]
            if not latest_query.lower().startswith("select "):
                raise ValueError("Only select queries are supported for registering featuring sets")
        except IndexError:
            raise ValueError("No query seems to have been executed in this session")
        return latest_query


class DeltaTable(DataSourceWrapper):
    def __init__(self, path, version=-1, timestamp=None, filter=None):
        self.path = path
        self.version = version
        self.timestamp = timestamp
        self.filter = filter
        if version and timestamp:
            raise ValueError("Only one of version or timestamp is supported")

    def get_raw_data_location(self, stub: CoreServiceStub):
        raw_data_location = pb.RawDataLocation()
        delta_table = pb.DeltaTableSpec()
        delta_table.path = self.path
        delta_table.version = self.version
        if self.timestamp:
            delta_table.timestamp = self.timestamp
        if self.filter:
            delta_table.filter.CopyFrom(self.filter._filter)
        raw_data_location.delta_table.CopyFrom(delta_table)
        return raw_data_location


class CSVFolder(FileDataSourceWrapper):
    def __init__(self, root_folder, delimiter=",", filter_pattern=""):
        super().__init__(root_folder)
        self.root_folder = root_folder
        self.filter_pattern = filter_pattern
        self.delimiter = delimiter

    def get_raw_data_location(self, stub: CoreServiceStub):
        if self.is_local():
            self._write_to_storage(stub, self.filter_pattern)
        raw_data_location = pb.RawDataLocation()
        csv_folder = pb.CSVFolderSpec()
        csv_folder.root_folder = self.external_path
        csv_folder.filter_pattern = self.filter_pattern
        csv_folder.delimiter = self.delimiter
        raw_data_location.csv_folder.CopyFrom(csv_folder)
        return raw_data_location


class ParquetFolder(FileDataSourceWrapper):
    def __init__(self, root_folder, filter_pattern=""):
        super().__init__(root_folder)
        self.root_folder = root_folder
        self.filter_pattern = filter_pattern

    def get_raw_data_location(self, stub: CoreServiceStub):
        if self.is_local():
            self._write_to_storage(stub, self.filter_pattern)
        raw_data_location = pb.RawDataLocation()
        parquet_folder = pb.ParquetFolderSpec()
        parquet_folder.root_folder = self.external_path
        parquet_folder.filter_pattern = self.filter_pattern
        raw_data_location.parquet_folder.CopyFrom(parquet_folder)
        return raw_data_location


class JSONFolder(FileDataSourceWrapper):
    def __init__(self, root_folder, multiline=False, filter_pattern=""):
        super().__init__(root_folder)
        self.root_folder = root_folder
        self.multiline = multiline
        self.filter_pattern = filter_pattern

    def get_raw_data_location(self, stub: CoreServiceStub):
        if self.is_local():
            self._write_to_storage(stub, self.filter_pattern)
        raw_data_location = pb.RawDataLocation()
        json_folder = pb.JSONFolderSpec()
        json_folder.root_folder = self.external_path
        json_folder.filter_pattern = self.filter_pattern
        json_folder.multiline = self.multiline
        raw_data_location.json_folder.CopyFrom(json_folder)

        return raw_data_location


class MongoDbCollection(DataSourceWrapper):
    def __init__(self, connection_uri="mongodb://localhost:27017/", database="", collection=""):
        if not database:
            raise ValueError("Database name is required!")
        if not collection:
            raise ValueError("Collection name is required!")
        self.connection_uri = connection_uri
        self.database = database
        self.collection = collection

    def get_raw_data_location(self, stub: CoreServiceStub):
        raw_data_location = pb.RawDataLocation()
        mongo = pb.MongoDbCollectionSpec()
        mongo.connection_uri = self.connection_uri
        mongo.database = self.database
        mongo.collection = self.collection
        raw_data_location.mongo_db.CopyFrom(mongo)

        return raw_data_location


class BigQueryTable(DataSourceWrapper):
    def __init__(
        self,
        table="",
        parent_project="",
        query="",
        materialization_dataset="",
    ):
        if not (table or query):
            raise ValueError("Table or query is required!")
        if table and query:
            raise ValueError("Only one of table or query is supported!")
        if query and not materialization_dataset:
            raise ValueError("When query is specified, then materialization_dataset is required!")
        self.table = table
        self.parent_project = parent_project
        self.query = query
        self.materialization_dataset = materialization_dataset

    def get_raw_data_location(self, stub: CoreServiceStub):
        raw_data_location = pb.RawDataLocation()
        google_big_query = pb.BigQueryTableSpec()
        google_big_query.table = self.table
        google_big_query.parent_project = self.parent_project
        google_big_query.query = self.query
        google_big_query.materialization_dataset = self.materialization_dataset
        raw_data_location.google_big_query.CopyFrom(google_big_query)
        return raw_data_location


def get_source(raw_data_location):
    if raw_data_location.HasField("csv"):
        csv = raw_data_location.csv
        return CSVFile(path=csv.path, delimiter=csv.delimiter)
    elif raw_data_location.HasField("json"):
        json = raw_data_location.json
        return JSONFile(path=json.path, multiline=json.multiline)
    elif raw_data_location.HasField("parquet"):
        parquet = raw_data_location.parquet
        return ParquetFile(path=parquet.path)
    elif raw_data_location.HasField("snowflake"):
        snowflake = raw_data_location.snowflake
        proxy = (
            Proxy(
                host=snowflake.proxy.host,
                port=snowflake.proxy.port,
                user=snowflake.proxy.user,
                password=snowflake.proxy.password,
            )
            if snowflake.HasField("proxy")
            else None
        )

        return SnowflakeTable(
            table=snowflake.table,
            database=snowflake.database,
            url=snowflake.url,
            warehouse=snowflake.warehouse,
            schema=snowflake.schema,
            query=snowflake.query,
            insecure=snowflake.insecure,
            role=snowflake.role,
            account=snowflake.account,
            proxy=proxy,
        )
    elif raw_data_location.HasField("jdbc"):
        jdbc = raw_data_location.jdbc
        partition_options = PartitionOptions(
            num_partitions=jdbc.num_partitions,
            partition_column=jdbc.partition_column,
            lower_bound=jdbc.lower_bound,
            upper_bound=jdbc.upper_bound,
            fetch_size=jdbc.fetch_size,
        )
        return JdbcTable(
            connection_url=jdbc.connection_url, table=jdbc.table, query=jdbc.query, partition_options=partition_options
        )
    elif raw_data_location.HasField("delta_table"):
        delta_table = raw_data_location.delta_table
        filter = delta_table.filter if (delta_table.HasField("filter")) else None
        return DeltaTable(
            path=delta_table.path, version=delta_table.version, timestamp=delta_table.timestamp, filter=filter
        )
    elif raw_data_location.HasField("csv_folder"):
        csv_folder = raw_data_location.csv_folder
        return CSVFolder(
            root_folder=csv_folder.root_folder, filter_pattern=csv_folder.filter_pattern, delimiter=csv_folder.delimiter
        )
    elif raw_data_location.HasField("parquet_folder"):
        parquet_folder = raw_data_location.parquet_folder
        return ParquetFolder(root_folder=parquet_folder.root_folder, filter_pattern=parquet_folder.filter_pattern)
    elif raw_data_location.HasField("json_folder"):
        json_folder = raw_data_location.json_folder
        return JSONFolder(
            root_folder=json_folder.root_folder,
            filter_pattern=json_folder.filter_pattern,
            multiline=json_folder.multiline,
        )
    elif raw_data_location.HasField("mongo_db"):
        mongo_db = raw_data_location.mongo_db
        return MongoDbCollection(
            connection_uri=mongo_db.connection_uri, database=mongo_db.database, collection=mongo_db.collection
        )
    elif raw_data_location.HasField("big_query"):
        big_query = raw_data_location.big_query
        return BigQueryTable(
            table=big_query.table,
            parent_project=big_query.parent_project,
            query=big_query.query,
            materialization_dataset=big_query.materialization_dataset,
        )
    else:
        raise Exception("Unsupported external data source.")
