from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile, UserProfile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'additional_profile'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
