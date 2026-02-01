import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError
from .serializers import VolunteerSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser,IsAuthenticatedOrReadOnly
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

    def get_permissions(self):
        # Anyone can VIEW projects
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]

        # Only admins can CREATE / UPDATE / DELETE
        return [permissions.IsAdminUser()]


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    permission_classes = [permissions.AllowAny]  # Anyone can submit

    def get_queryset(self):
        # Admin sees all donations
        if self.request.user.is_staff:
            return Donation.objects.all()
        # Non-admins only see approved donations
        return Donation.objects.filter(approved=True)

    def get_permissions(self):
        # Allow POST for anyone
        if self.request.method == 'POST':
            return [permissions.AllowAny()]
        # Allow GET for authenticated users
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [permissions.IsAuthenticated()]
        # Only admin/staff can PUT/PATCH/DELETE
        return [permissions.IsAdminUser()]

    def get_serializer_context(self):
        # Pass request to serializer
        context = super().get_serializer_context()
        context['request'] = self.request
        # Hide amount for non-admins
        if not self.request.user.is_staff:
            context['hide_amount'] = True
        return context

    def perform_create(self, serializer):
        # Optionally set donor if you have a logged-in user
        if self.request.user.is_authenticated:
            serializer.save(donor=self.request.user)
        else:
            serializer.save()

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
    """
    Handles volunteer submissions:
    - Anyone can GET approved volunteers and POST new volunteer applications.
    - Admin users can approve/reject or update any volunteer.
    """
    serializer_class = VolunteerSerializer

    def get_permissions(self):
        """
        - Admin users can update, partial_update, or delete.
        - Anyone else can list or create volunteer applications.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        - Admin sees all volunteers.
        - Non-admins see only approved volunteers.
        """
        user = self.request.user
        if user.is_staff:
            return Volunteer.objects.all().order_by("-date_joined")
        return Volunteer.objects.filter(status="approved").order_by("-date_joined")

    def perform_create(self, serializer):
        """
        Save volunteer application:
        - If the user is logged in, attach them.
        - Otherwise, allow anonymous submission.
        - Status is always 'pending' on creation.
        """
        serializer.save(
            user=self.request.user if self.request.user.is_authenticated else None,
            status="pending"
        )

        
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can view users

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer