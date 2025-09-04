# pylint: disable=unused-argument
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBudgetOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.has_access(
            request.user,
            request.method not in SAFE_METHODS,
            request.method == 'DELETE'
        )


class CanAccessBudgetShare(BasePermission):
    SHARED_USER_PERMISSIONS = SAFE_METHODS + ('DELETE',)

    def has_object_permission(self, request, view, obj):
        return (
            obj.user == request.user and request.method in self.SHARED_USER_PERMISSIONS
            or obj.budget.user == request.user
        )


class IsPayeeOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.budget.has_access(request.user, request.method not in SAFE_METHODS)


class IsPaymentOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.payee.budget.has_access(request.user, request.method not in SAFE_METHODS)
