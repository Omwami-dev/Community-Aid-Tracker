from aid.views import mpesa_donate
from .views import RegisterView
from .views import EmailTokenObtainPairView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, DonationViewSet, BeneficiaryViewSet, VolunteerViewSet, UserViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'donations', DonationViewSet)
router.register(r'beneficiaries', BeneficiaryViewSet)
router.register(r'volunteers', VolunteerViewSet, basename='volunteer') 
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("donate/mpesa/", mpesa_donate),
    path("register/", RegisterView.as_view(), name="register"),
    path("api/token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
]

urlpatterns += router.urls
