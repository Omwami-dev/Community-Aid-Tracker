from rest_framework import serializers
from .models import Project, Donation, Beneficiary, Volunteer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    # Use project ID instead of title
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all()
    )

    class Meta:
        model = Donation
        fields = [
            'id', 'donor_name', 'donor_email', 'donor_phone',
            'project', 'amount', 'message', 'approved', 'date'
        ]
        read_only_fields = ['approved', 'date']

    def create(self, validated_data):
        # Automatically assign the donor as the current user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['donor'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if request and not request.user.is_staff:
            data["amount"] = "Hidden until admin approves"
        return data
class BeneficiarySerializer(serializers.ModelSerializer):
    # Readable project title for frontend
    project_name = serializers.CharField(source='project.title', read_only=True)

    # Accept project by title when creating/updating
    project = serializers.SlugRelatedField(
        slug_field='title',
        queryset=Project.objects.all()
    )

    class Meta:
        model = Beneficiary
        fields = ['id', 'name', 'contact', 'project', 'project_name', 'approved', 'date_created']
        read_only_fields = ['id', 'project_name', 'date_created']
class VolunteerSerializer(serializers.ModelSerializer):
    # Use project title instead of ID
    project = serializers.SlugRelatedField(
        slug_field='title',
        queryset=Project.objects.all()
    )
    project_name = serializers.CharField(source='project.title', read_only=True)

    class Meta:
        model = Volunteer
        fields = [
            'id',
            'user',         # Optional
            'name',
            'email',
            'profession',
            'project',
            'project_name',
            'role',
            'status',
            'date_joined',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'date_joined',
            'project_name',
        ]

    # Enforce required fields
    def validate_role(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("Role must be provided.")
        return value

    def validate_name(self, value):
        return value or "Anonymous"

    def validate_email(self, value):
        return value or "unknown@example.com"

    def validate_profession(self, value):
        return value or "Not specified"

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)   # <-- IMPORTANT
        user.save()
        return user

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        return user
    
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # Authenticate with email
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        # Required by Simple JWT
        data = super().validate({"username": user.username, "password": password})
        return data