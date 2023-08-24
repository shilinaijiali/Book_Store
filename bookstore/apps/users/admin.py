from django.contrib import admin

from users.models import UserProfile


@admin.register(UserProfile)
class UserAdmin(admin.ModelAdmin):
    pass