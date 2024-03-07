from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
import admin_thumbnails

from .models import Account, UserProfile


# Register your models here.


class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined','is_active')
    list_display_links = ('email', 'first_name', 'last_name', 'username')
    readonly_fields = ('password', 'last_login', 'date_joined')
    ordering = ('-date_joined', 'email')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

@admin_thumbnails.thumbnail('profile_picture') #Add preview for 'profile_picture' model field 
class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html(f'<img src="{object.get_profile_picture_url()}" width="30" height="30" style="border-radius: 50%;">')
    
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

