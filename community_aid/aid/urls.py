from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, DonationViewSet, BeneficiaryViewSet, VolunteerViewSet, UserViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'donations', DonationViewSet)
router.register(r'beneficiaries', BeneficiaryViewSet)
router.register(r'volunteers', VolunteerViewSet)
router.register(r'users', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
