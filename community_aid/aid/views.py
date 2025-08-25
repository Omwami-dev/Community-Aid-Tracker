from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Project, Donation, Beneficiary, Volunteer
from .serializers import ProjectSerializer, DonationSerializer, BeneficiarySerializer, VolunteerSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow read-only to anyone, but only admins can modify.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can access


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users

    def get_serializer_context(self):
        # Pass request to serializer so it can check if user is admin
        context = super().get_serializer_context()
        context['request'] = self.request
        return context



class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Public can view, only logged-in users can modify
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Beneficiary.objects.all()
        return Beneficiary.objects.filter(approved=True)

    def perform_create(self, serializer):
        serializer.save(approved=False)  # Always save as unapproved
    
    def perform_update(self, serializer):
        # Only admins can update/edit beneficiaries
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can update beneficiaries.")
        serializer.save()

    def perform_destroy(self, instance):
        # Only admins can delete beneficiaries
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can delete beneficiaries.")
        instance.delete()

class VolunteerViewSet(viewsets.ModelViewSet):
    queryset = Volunteer.objects.all()
    serializer_class = VolunteerSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can access

