from rest_framework.permissions import BasePermission, SAFE_METHODS

# PROJECT PERMISSIONS
class IsProjectOwnerOrReadOnly(BasePermission):
    """
    Allow anyone to read projects.
    Only project creator or admin can edit/delete.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        # Only creator or admin can update/delete
        return obj.created_by == request.user or request.user.is_staff

# DONATION PERMISSIONS
class IsDonationOwnerOrAdmin(BasePermission):
    """
    Donors can only see their own donations.
    Admins can see all.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.donor == request.user

# BENEFICIARY PERMISSIONS
class IsBeneficiaryOrAdmin(BasePermission):
    """
    Beneficiaries can only view/update their own record.
    Admins can view/edit all.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user  # assuming Beneficiary has a FK to User


class CanApproveBeneficiary(BasePermission):
    """
    Only admins can approve beneficiaries.
    """
    def has_permission(self, request, view):
        if view.action == "approve":  # custom action
            return request.user.is_staff
        return True

# VOLUNTEER PERMISSIONS
class IsVolunteerOrAdmin(BasePermission):
    """
    Volunteers can only manage their own record.
    Admins can manage all.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user == request.user
