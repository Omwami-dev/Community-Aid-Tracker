from rest_framework import serializers
from .models import Project, Donation, Beneficiary, Volunteer
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

class DonationSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField()  # conditional field

    class Meta:
        model = Donation
        fields = '__all__'

    def get_amount(self, obj):
        request = self.context.get('request')
        if request and request.user.is_staff:
            return obj.amount
        return None  # hides amount for non-admins
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