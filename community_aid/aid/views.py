from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Project, Donation, Beneficiary, Volunteer
from .serializers import ProjectSerializer, DonationSerializer, BeneficiarySerializer, VolunteerSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can access


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can access donations

class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Public can view, only logged-in users can modify


class VolunteerViewSet(viewsets.ModelViewSet):
    queryset = Volunteer.objects.all()
    serializer_class = VolunteerSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only logged-in users can access

