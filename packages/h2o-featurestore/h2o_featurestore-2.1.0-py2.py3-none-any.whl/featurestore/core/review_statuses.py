from ai.h2o.featurestore.api.v1 import CoreService_pb2 as pb

IN_PROGRESS = pb.ReviewStatus.REVIEW_STATUS_TO_REVIEW
APPROVED = pb.ReviewStatus.REVIEW_STATUS_APPROVED
REJECTED = pb.ReviewStatus.REVIEW_STATUS_REJECTED
