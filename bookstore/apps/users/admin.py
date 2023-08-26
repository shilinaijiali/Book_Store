from django.contrib import admin

from apps.users.models import UserProfile


@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
    pass