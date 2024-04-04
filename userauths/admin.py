from django.contrib import admin
from userauths.models import User, ContactUs, Profile

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email", "bio"]


class ContactUsAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "subject"]


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "bio", "phone", "verified"]
    list_editable = [
        "verified",
    ]


admin.site.register(User, UserAdmin)
admin.site.register(ContactUs, ContactUsAdmin)
admin.site.register(Profile, ProfileAdmin)
