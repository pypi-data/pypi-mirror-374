import ai.h2o.featurestore.api.v1.CoreService_pb2 as pb

from .permission_base import PermissionBase
from .user import User


class PermissionRequest(PermissionBase):
    @property
    def user(self):
        return User(self._permission.user)

    def withdraw(self):
        """Withdraw a previously raised permission request.

        Typical example:
            request.withdraw()

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.htm
        """
        request = pb.WithdrawPendingPermissionRequest(permission_id=self._permission.id)
        self._stub.WithdrawPendingPermission(request)


class ManageablePermissionRequest(PermissionRequest):
    @property
    def requestor(self):
        """User who raised the specific permission request."""
        return User(self._permission.user)

    def approve(self, reason):
        """Approve a permission request.

        Args:
            reason: (str) A reason for permission request approval.

        Typical example:
            manageable_request.approve("it will be fun")

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        request = pb.ApprovePendingPermissionRequest(permission_id=self._permission.id, reason=reason)
        self._stub.ApprovePendingPermission(request)

    def reject(self, reason):
        """Reject a permission request.

        Args:
            reason: (str) A reason for permission request rejection.

        Typical example:
            manageable_request.reject("it's not ready yet")

        For more details:
            https://docs.h2o.ai/featurestore/api/permissions.html#managing-permission-requests-from-other-users
        """
        request = pb.RejectPendingPermissionRequest(permission_id=self._permission.id, reason=reason)
        self._stub.RejectPendingPermission(request)
