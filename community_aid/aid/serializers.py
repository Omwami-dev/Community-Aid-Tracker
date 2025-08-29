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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']