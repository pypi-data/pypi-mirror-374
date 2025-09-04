import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from ..entities.ingest import Ingest


class IngestHistory:
    def __init__(self, stub, feature_set):
        self._feature_set = feature_set
        self._stub = stub
        self._ingest_history = self.__load_history()

    def list(self):
        """Return a list of ingestion.

        Returns:
            list[Ingest]: A collection of ingestion.

        Typical example:
            history = my_feature_set.ingest_history()
            history.list()

        For more details:
            https://docs.h2o.ai/featurestore/api/ingest_history_api.html#getting-the-ingestion-history
        """
        return [Ingest(self._stub, self._feature_set, ingest) for ingest in self._ingest_history]

    def refresh(self):
        """Refresh ingest history object with the latest ingestion (if there are any).

        Typical example:
            history = my_feature_set.ingest_history()
            history.refresh()
        """
        self._ingest_history = self.__load_history()

    @property
    def size(self):
        """A size of history."""
        return len(self._ingest_history)

    @property
    def first(self):
        """A first ingestion."""
        if self.list():
            return Ingest(self._stub, self._feature_set, self._ingest_history[0])
        else:
            raise Exception("No ingest has been performed so far.")

    @property
    def last(self):
        """A last ingestion."""
        if self.list():
            return Ingest(self._stub, self._feature_set, self._ingest_history[-1])
        else:
            raise Exception("No ingest has been performed so far.")

    def get(self, ingest_id):
        """Obtain a specific ingestion.

        Args:
            ingest_id: (str) A unique id of ingestion.

        Returns:
            Ingest: An existing ingestion.

        Typical example:
            history = my_feature_set.ingest_history()
            specific_ingest = history.get(ingest_id)

        Raises:
            Exception: No ingest has been found for the given ingest id.
        """
        ingests = [ingest for ingest in self._ingest_history if ingest.ingest_id == ingest_id]
        if ingests:
            return Ingest(self._stub, self._feature_set, ingests[0])
        else:
            raise Exception("No ingest has been found for the ingest id " + ingest_id)

    def __load_history(self):
        request = pb.GetIngestHistoryRequest()
        request.feature_set_id = self._feature_set.id
        request.feature_set_version = self._feature_set.version
        response = self._stub.GetIngestHistory(request)
        return response.ingest_history
