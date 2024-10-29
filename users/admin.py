from django.contrib import admin
from .models import User, EmailVerification

admin.site.register(User)
admin.site.register(EmailVerification)

# @admin.register(User)
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username',)
#     inlines = (BasketAdmin,)