from django.contrib import admin

from accounts.models import Profile, Security


admin.site.register(Profile)
admin.site.register(Security)
