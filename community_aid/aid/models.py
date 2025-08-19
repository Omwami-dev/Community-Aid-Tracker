from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Override ManyToMany fields with related_name to avoid clashes
    groups = models.ManyToManyField(
        related_name="custom_user_set",  # changed name
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        related_name="custom_user_permissions_set",  # changed name
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Beneficiary(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    contact_info = models.CharField(max_length=200)

class Volunteer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=100)
    date_joined = models.DateTimeField(auto_now_add=True)
