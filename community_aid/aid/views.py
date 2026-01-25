import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Project, Donation, Beneficiary, Volunteer
from .serializers import ProjectSerializer, UserSerializer, DonationSerializer, BeneficiarySerializer,VolunteerSerializer, UserSerializer
from django.contrib.auth import get_user_model
from .permissions import (
    IsProjectOwnerOrReadOnly,
    IsDonationOwnerOrAdmin,
    IsBeneficiaryOrAdmin,
    IsVolunteerOrAdmin,
)

User = get_user_model()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mpesa_donate(request):
    """
    Initiates an M-Pesa payment via Flutterwave for a specific project
    """
    amount = request.data.get("amount")
    phone = request.data.get("phone")
    project_id = request.data.get("projectId")

    if not all([amount, phone, project_id]):
        return Response({"error": "All fields are required"}, status=400)

    # Get the project
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found"}, status=404)

    # Prepare payload for Flutterwave
    payload = {
        "tx_ref": f"donation_{request.user.id}_{project_id}",
        "amount": amount,
        "currency": "KES",
        "payment_type": "mpesa",
        "customer": {
            "email": request.user.email,
            "phonenumber": phone,
            "name": request.user.username,
        },
        "customizations": {
            "title": "Community Aid Donation",
            "description": f"Donation to {project.title}",
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}"
    }

    try:
        # Call Flutterwave API
        response = requests.post(
            "https://api.flutterwave.com/v3/payments",
            json=payload,
            headers=headers,
            timeout=30
        )
        response_data = response.json()
    except requests.RequestException as e:
        return Response({"error": "Payment request failed", "details": str(e)}, status=500)

    # Save donation as pending in database
    Donation.objects.create(
        donor=request.user,
        project=project,
        amount=amount,
        payment_method="mpesa",
        status="pending"
    )

    return Response(response_data)


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
    permission_classes = [IsProjectOwnerOrReadOnly]


    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [IsDonationOwnerOrAdmin]


    def get_permissions(self):
        # Allow GET for all authenticated users
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.IsAuthenticated()]
        # Only admin/staff for create/update/delete
        return [permissions.IsAdminUser()]

    def get_serializer_context(self):
        # Pass request to serializer so it can check if user is admin
        context = super().get_serializer_context()
        context['request'] = self.request
        # Add hide_amount flag for non-admins
        if not self.request.user.is_staff:
            context['hide_amount'] = True
        return context




class BeneficiaryViewSet(viewsets.ModelViewSet):
    queryset = Beneficiary.objects.all()
    serializer_class = BeneficiarySerializer
    permission_classes = [IsBeneficiaryOrAdmin]


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
    permission_classes = [IsVolunteerOrAdmin]

    def get_queryset(self):
        # Admin sees all volunteers
        if self.request.user.is_staff:
            return Volunteer.objects.all()
        
        # Everyone else sees only approved volunteers
        return Volunteer.objects.filter(status="approved")

    def perform_create(self, serializer):
        # When a volunteer applies, status must be pending
        serializer.save(status="pending")


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can view users

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]