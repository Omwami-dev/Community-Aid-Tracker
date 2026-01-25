from rest_framework import serializers
from .models import Project, Donation, Beneficiary, Volunteer
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    donor = serializers.SlugRelatedField(
        slug_field="username",  # use the username instead of ID
        queryset=User.objects.all()  # allows searching donor by username
    )
    project = serializers.SlugRelatedField(
        slug_field="title",      # now you can type project title
        queryset=Project.objects.all()
    )
    class Meta:
        model = Donation
        fields = '__all__'  # includes project, donor, amount, etc.
        extra_kwargs = {
            "amount": {"required": True},  # makes sure amount must be provided
        }
class BeneficiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Beneficiary
        fields = '__all__'

class VolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volunteer
        fields = '__all__'
        read_only_fields = ["status"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']

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