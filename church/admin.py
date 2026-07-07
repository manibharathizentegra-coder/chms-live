from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

@admin.register(Oauth)
class OauthAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "refresh_token",
        "status",
        "created_at_ist",
        "modified_at_ist",
    )

    def created_at_ist(self, obj):
        return obj.created_at.strftime("%d-%m-%Y %I:%M %p")

    created_at_ist.short_description = "Created At"

    def modified_at_ist(self, obj):
        return obj.modify_at.strftime("%d-%m-%Y %I:%M %p")

    modified_at_ist.short_description = "Modified At"