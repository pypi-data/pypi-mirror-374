import os
from enum import Enum

import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from .. import interactive_console
from ..utils import Utils


class Artifact:
    def __init__(self, artifact, stub):
        self._artifact = artifact
        self._stub = stub

    @property
    def id(self):
        return self._artifact.artifact_id

    @property
    def title(self):
        return self._artifact.title

    @property
    def description(self):
        return self._artifact.description

    @property
    def artifact_type(self):
        return ArtifactType.from_proto(self._artifact.artifact_type)

    def delete(self):
        request = pb.DeleteArtifactRequest(artifact_id=self._artifact.artifact_id)
        self._stub.DeleteArtifact(request)
        interactive_console.log(f"Artifact '{self._artifact.title}' was deleted")

    def __repr__(self):
        return Utils.pretty_print_proto(self._artifact)


class FileArtifact(Artifact):
    def __init__(self, artifact, stub):
        super(FileArtifact, self).__init__(artifact, stub)

    @property
    def filename(self):
        return self._artifact.filename

    @property
    def upload_status(self):
        return ArtifactUploadStatus.from_proto(self._artifact.upload_status)

    def retrieve(self, filepath, overwrite_existing_file="n"):
        if not Utils.filepath_directory_exists(filepath):
            raise Exception(f"Can't save artifact as path does not exist: '{filepath}'")

        interactive_console.log("Requesting download link")
        request = pb.RetrieveArtifactRequest(artifact_id=self._artifact.artifact_id)
        response = self._stub.RetrieveArtifact(request)

        destination = os.path.join(filepath, response.artifact.filename) if os.path.isdir(filepath) else filepath
        if os.path.exists(destination) and overwrite_existing_file.lower() != "y":
            raise Exception(f"Artifact already exists '{destination}'")

        interactive_console.log("Downloading content")
        Utils.download_file(destination, response.artifact.url)
        interactive_console.log(f"Artifact '{self._artifact.title}' was saved into '{destination}'")


class LinkArtifact(Artifact):
    def __init__(self, artifact, stub):
        super(LinkArtifact, self).__init__(artifact, stub)

    @property
    def url(self):
        return self._artifact.url


class ArtifactFactory:
    @staticmethod
    def create_acrtifact(artifact, stub):
        if artifact.artifact_type == ArtifactType.ARTIFACT_TYPE_FILE.value:
            return FileArtifact(artifact, stub)
        elif artifact.artifact_type == ArtifactType.ARTIFACT_TYPE_LINK.value:
            return LinkArtifact(artifact, stub)
        else:
            raise Exception("Unknown artifact type encountered!")


class ArtifactType(Enum):
    ARTIFACT_TYPE_UNSPECIFIED = 0
    ARTIFACT_TYPE_LINK = 1
    ARTIFACT_TYPE_FILE = 2

    @classmethod
    def from_proto(cls, proto_artifacts_type):
        return {
            pb.ArtifactType.ARTIFACT_TYPE_UNSPECIFIED: cls.ARTIFACT_TYPE_UNSPECIFIED,
            pb.ArtifactType.ARTIFACT_TYPE_LINK: cls.ARTIFACT_TYPE_LINK,
            pb.ArtifactType.ARTIFACT_TYPE_FILE: cls.ARTIFACT_TYPE_FILE,
        }[proto_artifacts_type]


class ArtifactUploadStatus(Enum):
    ARTIFACT_UPLOAD_STATUS_NOT_APPLICABLE = 0
    ARTIFACT_UPLOAD_STATUS_IN_PROGRESS = 1
    ARTIFACT_UPLOAD_STATUS_DONE = 2
    ARTIFACT_UPLOAD_STATUS_FAILED = 3

    @classmethod
    def from_proto(cls, proto_upload_status):
        return {
            pb.ArtifactUploadStatus.ARTIFACT_UPLOAD_STATUS_NOT_APPLICABLE: cls.ARTIFACT_UPLOAD_STATUS_NOT_APPLICABLE,
            pb.ArtifactUploadStatus.ARTIFACT_UPLOAD_STATUS_IN_PROGRESS: cls.ARTIFACT_UPLOAD_STATUS_IN_PROGRESS,
            pb.ArtifactUploadStatus.ARTIFACT_UPLOAD_STATUS_DONE: cls.ARTIFACT_UPLOAD_STATUS_DONE,
            pb.ArtifactUploadStatus.ARTIFACT_UPLOAD_STATUS_FAILED: cls.ARTIFACT_UPLOAD_STATUS_FAILED,
        }[proto_upload_status]
