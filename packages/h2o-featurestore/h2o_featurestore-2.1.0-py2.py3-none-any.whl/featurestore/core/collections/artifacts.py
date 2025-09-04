import os

import requests

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from .. import interactive_console
from ..entities.artifact import ArtifactFactory, FileArtifact, LinkArtifact
from ..utils import Utils


class Artifacts:
    def __init__(self, feature_set, stub):
        self._feature_set = feature_set
        self._stub = stub
        self._feature_set_major_version = int(feature_set.version.split(".")[0])

    def store_file(self, file_path, title=None, description=None):
        store_response = self._request_backend_storage(file_path, title, description)
        interactive_console.log("Uploading file content")
        self._upload_content(file_path, store_response)
        retrieve_response = self._retrieve_artifact(store_response)
        interactive_console.log(f"File: {file_path} was successfully uploaded")
        return FileArtifact(retrieve_response.artifact, self._stub)

    def _request_backend_storage(self, file_path, title, description):
        file_name = os.path.basename(file_path)
        checksum = Utils.generate_md5_checksum(file_path)
        request = pb.StoreFileArtifactRequest(
            title=title or f"File {file_name}",
            description=description or "user uploaded file",
            filename=file_name,
            feature_set_id=self._feature_set.id,
            feature_set_major_version=self._feature_set_major_version,
            md5_checksum=checksum,
        )
        store_response = self._stub.StoreFileArtifact(request)
        return store_response

    def _upload_content(self, file_path, store_response):
        self._update_status(store_response.artifact_id, pb.ArtifactUploadStatus.ARTIFACT_UPLOAD_STATUS_IN_PROGRESS)
        with open(file_path, "rb") as file:
            data_response = requests.put(
                url=store_response.url,
                data=file,
                headers=store_response.headers,
            )
            if data_response.status_code not in range(200, 300):
                self._update_status(store_response.artifact_id, pb.ArtifactUploadStatus.ARTIFACT_UPLOAD_STATUS_FAILED)

                raise Exception(
                    f"File upload failed with status code {data_response.status_code} "
                    f"and message {data_response.text}"
                )
        self._update_status(store_response.artifact_id, pb.ArtifactUploadStatus.ARTIFACT_UPLOAD_STATUS_DONE)

    def _retrieve_artifact(self, store_response):
        retrieve_request = pb.RetrieveArtifactRequest(artifact_id=store_response.artifact_id)
        retrieve_response = self._stub.RetrieveArtifact(retrieve_request)
        return retrieve_response

    def _update_status(self, artifact_id, status):
        status_update_request = pb.UpdateUploadStatusRequest(artifact_id=artifact_id, upload_status=status)
        self._stub.UpdateUploadStatus(status_update_request)

    def store_link(self, url, title=None, description=None):
        upload_response = self._upload_link(url, title, description)
        retrieve_response = self._retrieve_artifact(upload_response)
        interactive_console.log(f"Link: {url} was successfully uploaded")
        return LinkArtifact(retrieve_response.artifact, self._stub)

    def _upload_link(self, url, title, description):
        request = pb.StoreLinkRequest(
            title=title or f"Link {url}",
            description=description or "user uploaded link",
            url=url,
            feature_set_id=self._feature_set.id,
            feature_set_major_version=self._feature_set_major_version,
        )
        response = self._stub.StoreLink(request)
        return response

    def list(self):
        """Return a generator which obtains artifacts associated with the feature set, lazily.

        Returns:
            Iterable[Artifact]: A generator iterator object consists of artifacts.

        Typical example:
            feature_set.artifacts.list()
        """
        request = pb.ListArtifactsRequest(
            feature_set_id=self._feature_set.id, feature_set_major_version=self._feature_set_major_version
        )
        while request:
            response = self._stub.ListArtifacts(request)
            if response.next_page_token:
                request.page_token = response.next_page_token
            else:
                request = None
            for artifact in response.artifacts:
                yield ArtifactFactory.create_acrtifact(artifact, self._stub)

    def __repr__(self):
        return "This class wraps together methods working with feature set artifacts"
