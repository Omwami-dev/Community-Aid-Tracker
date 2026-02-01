from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings 
from django.utils import timezone

class User(AbstractUser):
     email = models.EmailField(unique=True)
     date_of_birth = models.DateField(null=True, blank=True)
     profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)

    # Override ManyToMany fields with related_name to avoid clashes
     groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # changed name
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
     USERNAME_FIELD = "email"          
     REQUIRED_FIELDS = ["username"]    

     user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions_set",  # changed name
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

     def __str__(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
class Project(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

     # Optional extra fields
    status = models.CharField(max_length=20, default="active")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Donation(models.Model):
    donor_name = models.CharField(max_length=100, default="Anonymous")
    donor_email = models.EmailField(default="unknown@example.com")
    donor_phone = models.CharField(max_length=20, blank=True, null=True)
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)  
    message = models.TextField(blank=True, null=True)  # optional message from donor

    def __str__(self):
        return f"{self.donor.username} - {self.amount} to {self.project.name}"

class Beneficiary(models.Model):
    project = models.ForeignKey(
        "Project",
        on_delete=models.CASCADE,
        related_name="beneficiaries"
    )
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=200)  # renamed from contact_info for simplicity
    approved = models.BooleanField(default=False)  # Admin approval required
    date_created = models.DateTimeField(auto_now_add=True)  # Optional: track creation date

    def __str__(self):
        return f"{self.name} - {self.project.title}"
    
class Volunteer(models.Model):
    # Optional user reference (anonymous volunteers can submit)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Fields for anonymous volunteers
    name = models.CharField(max_length=255, default="Anonymous")
    email = models.EmailField(default="unknown@example.com")
    profession = models.CharField(max_length=255, default="Not specified")

    # Volunteer role & project
    role = models.CharField(max_length=100)
    project = models.ForeignKey("Project", on_delete=models.CASCADE)

    # Status & timestamps
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.project.title}"
