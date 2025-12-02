from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import UserProfile, AdminRole, GalleryImage


class AdminRoleInline(admin.StackedInline):
	model = AdminRole
	can_delete = False
	verbose_name = 'Admin role'
	verbose_name_plural = 'Admin role'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'age', 'county', 'constituency', 'contact_info')
	search_fields = ('user__username', 'user__email', 'county', 'constituency')


# Unregister default User admin and re-register with AdminRole inline
admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	inlines = (AdminRoleInline,)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
	list_display = ('id', 'trip', 'uploaded_by', 'caption', 'image_preview')
	readonly_fields = ('image_preview',)
	search_fields = ('trip__title', 'uploaded_by__username')

	def image_preview(self, obj):
		if obj.image_url:
			return f"<img src='{obj.image_url.url}' style='max-height:100px;'/>"
		return ''
	image_preview.allow_tags = True
	image_preview.short_description = 'Preview'
