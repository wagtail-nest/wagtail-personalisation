from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from sandbox.apps.user import forms, models


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    form = forms.UserChangeForm
    add_form = forms.UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["email"]
    list_filter = ["is_superuser"]

    fieldsets = (
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name"]}),
        (
            "Permissions",
            {
                "fields": [
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ]
            },
        ),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ["email", "password1", "password2"]}),
    )
    search_fields = ["first_name", "last_name", "email"]
    ordering = ["email"]
    filter_horizontal = []
