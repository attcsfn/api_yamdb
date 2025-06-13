from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username__exact', 'email__exact')
    ordering = ('-date_joined',)
    date_hierarchy = 'date_joined'
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'bio')}),
        (_('Permissions'), {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
        }),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'role',
                'is_active',
                'is_staff',
                'is_superuser'
            ),
        }),
    )
    actions = ['activate_users', 'deactivate_users']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_admin:
            return qs.filter(is_superuser=False)
        return qs

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not request.user.is_admin:
            return readonly_fields + ('role', 'is_superuser')
        return readonly_fields

    def has_add_permission(self, request):
        return request.user.is_admin

    def has_delete_permission(self, request, obj=None):
        return request.user.is_admin

    @admin.action(description=_('Activate selected users'))
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_('Deactivate selected users'))
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
