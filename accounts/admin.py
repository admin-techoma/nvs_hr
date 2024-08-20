from django.contrib import admin
from django.contrib.auth import get_user_model
from import_export import resources
from import_export.admin import ImportExportModelAdmin

User = get_user_model()

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser')  # Adjust fields as needed

# Unregister the default UserAdmin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
admin.site.unregister(User)

@admin.register(User)
class UserAdmin(ImportExportModelAdmin, DefaultUserAdmin):
    resource_class = UserResource
    list_display = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_superuser']
    search_fields = ['username', 'email']
    list_filter = ['is_active', 'is_superuser']
    ordering = ['username']
    # Ensure to include fields from DefaultUserAdmin if needed
    fieldsets = DefaultUserAdmin.fieldsets
    add_fieldsets = DefaultUserAdmin.add_fieldsets
    filter_horizontal = DefaultUserAdmin.filter_horizontal
