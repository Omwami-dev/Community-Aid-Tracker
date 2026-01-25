# aid/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Project, Donation, Beneficiary, Volunteer

# Register custom User with standard UserAdmin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Add extra fields to the admin interface
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("date_of_birth", "profile_photo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional Info", {"fields": ("date_of_birth", "profile_photo")}),
    )
    search_fields = ["username", "email"]


# Register other models
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "start_date", "end_date", "created_by")
    search_fields = ("title", "description", "status")
    list_filter = ("status", "start_date", "end_date")


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("donor", "project", "amount", "date")
    search_fields = ("donor__username", "project__title")
    list_filter = ("date",)
    autocomplete_fields = ["donor", "project"]


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "contact_info")
    search_fields = ("name", "project__title")
    list_filter = ("approved",)  # Filter by approved/unapproved in admin panel
    actions = ["approve_selected"]

    def approve_selected(self, request, queryset):   # noqa: ARG001
        queryset.update(approved=True)
    approve_selected.short_description = "Approve selected beneficiaries"


# 🔥 Volunteer Admin with approval actions (added only, rest remains same)
@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "role", "status", "date_joined")
    search_fields = ("user__username", "project__title", "role")
    list_filter = ("status", "date_joined", "project")

    actions = ["approve_selected", "reject_selected"]

    def approve_selected(self, request, queryset):  # noqa: ARG001
     queryset.update(status="approved")
    approve_selected.short_description = "Approve selected volunteers"

    def reject_selected(self, request, queryset):  # noqa: ARG001
     queryset.update(status="rejected")
    reject_selected.short_description = "Reject selected volunteers"


