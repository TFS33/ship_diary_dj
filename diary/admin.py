from django.contrib import admin
from .models import (
    Ship,
    LogEntry,
    EngineLog,
    FuelLog,
    NavigationLog,
    WeatherLog,
    CrewLog,
    CustomUser,
)
from django.contrib.auth.admin import UserAdmin


# class DiaryAdmin(admin.ModelAdmin):
#     list_display = ['']
#     list_filter = ['']
#     fields = ['']
#     inlines = []
#     raw_id_fields = ['']
#     readonly_fields = ['']
#     search_fields = ['']
#     ordering = ['']


class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "first_name", "last_name", "date_joined"]
    ordering = ["email"]
    search_fields = ["email", "username", "first_name", "last_name"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )


# admin.site.register('Diary', DiaryAdmin)
admin.site.register(Ship)
admin.site.register(LogEntry)
admin.site.register(EngineLog)
admin.site.register(FuelLog)
admin.site.register(NavigationLog)
admin.site.register(WeatherLog)
admin.site.register(CrewLog)
admin.site.register(CustomUser, UserAdmin)
