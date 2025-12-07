from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import UserProfile, AdminRole, GalleryImage, Trip, Booking, TeamMember, TripType, TripCategory, Like, Comment, CommentLike
from .models import SentEmail


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
	list_display = ('id', 'trip_display', 'media_type', 'uploaded_by', 'caption_preview', 'created_at', 'image_preview')
	readonly_fields = ('image_preview', 'uploaded_by', 'created_at')
	search_fields = ('trip__title', 'uploaded_by__username', 'caption')
	list_filter = ('media_type', 'created_at', 'trip')
	fieldsets = (
		('Media Information', {
			'fields': ('trip', 'media_type', 'image_url', 'video_url', 'caption')
		}),
		('Metadata', {
			'fields': ('uploaded_by', 'created_at', 'image_preview'),
			'classes': ('collapse',)
		}),
	)

	def trip_display(self, obj):
		"""Display trip with type and status"""
		if obj.trip:
			trip_type = f" [{obj.trip.trip_type.get_name_display()}]" if obj.trip.trip_type else ""
			status = f" - {obj.trip.get_status_display()}"
			return f"{obj.trip.title}{trip_type}{status}"
		return "No Trip"
	trip_display.short_description = 'Trip'
	
	def caption_preview(self, obj):
		"""Show first 50 chars of caption"""
		if obj.caption:
			return obj.caption[:50] + ('...' if len(obj.caption) > 50 else '')
		return '-'
	caption_preview.short_description = 'Caption'

	def image_preview(self, obj):
		if obj.media_type == 'image' and obj.image_url:
			return f"<img src='{obj.image_url.url}' style='max-height:150px;'/>"
		elif obj.media_type == 'video' and obj.video_url:
			return f"<video style='max-height:150px;' controls><source src='{obj.video_url.url}' type='video/mp4'></video>"
		return 'No media'
	image_preview.allow_tags = True
	image_preview.short_description = 'Preview'
	
	def save_model(self, request, obj, form, change):
		"""Auto-set the uploaded_by field"""
		if not change:
			obj.uploaded_by = request.user
		super().save_model(request, obj, form, change)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
	list_display = ('title', 'trip_type', 'location', 'price', 'status', 'start_date', 'end_date')
	list_filter = ('status', 'trip_type', 'date')
	search_fields = ('title', 'location', 'description_short')
	fieldsets = (
		('Basic Information', {
			'fields': ('title', 'trip_type', 'location', 'price')
		}),
		('Trip Dates', {
			'fields': ('start_date', 'end_date'),
			'description': 'Set start and end dates to display trip duration (e.g., 2 nights 3 days)'
		}),
		('Description', {
			'fields': ('description_short', 'description_full')
		}),
		('Media', {
			'fields': ('image_url',)
		}),
		('Status', {
			'fields': ('status', 'featured')
		}),
	)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "trip", "amount", "status", "mpesa_receipt")
    list_filter = ("status",)
    search_fields = ("user__username", "trip__title", "mpesa_receipt")

# admin.site.register(Booking, BookingAdmin)



@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
	list_display = ('name', 'position', 'contact', 'order')
	fieldsets = (
		('Personal Information', {
			'fields': ('name', 'position', 'contact')
		}),
		('Details', {
			'fields': ('bio', 'image', 'order')
		}),
		('Metadata', {
			'fields': ('created_at',),
			'classes': ('collapse',)
		}),
		)
	readonly_fields = ('created_at',)


@admin.register(TripType)
class TripTypeAdmin(admin.ModelAdmin):
	list_display = ('get_name_display', 'description')
	fields = ('name', 'description')


@admin.register(TripCategory)
class TripCategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
	list_display = ('user', 'image_display', 'created_at')
	readonly_fields = ('created_at',)
	search_fields = ('user__username', 'image__caption')
	list_filter = ('created_at', 'image__trip')
	
	def image_display(self, obj):
		return f"{obj.image.trip.title} - {obj.image.get_media_type_display()}"
	image_display.short_description = 'Media'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
	list_display = ('user', 'image_display', 'comment_preview', 'time', 'is_reply')
	readonly_fields = ('time',)
	search_fields = ('user__username', 'comment', 'image__caption')
	list_filter = ('time', 'image__trip', 'parent_comment')
	
	def image_display(self, obj):
		return f"{obj.image.trip.title} - {obj.image.get_media_type_display()}"
	image_display.short_description = 'Media'
	
	def comment_preview(self, obj):
		return obj.comment[:50] + ('...' if len(obj.comment) > 50 else '')
	comment_preview.short_description = 'Comment'


@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
	list_display = ('user', 'comment_preview', 'like_type', 'created_at')
	readonly_fields = ('created_at',)
	search_fields = ('user__username', 'comment__comment')
	list_filter = ('is_like', 'created_at')
	
	def comment_preview(self, obj):
		preview = obj.comment.comment[:40]
		return preview + ('...' if len(obj.comment.comment) > 40 else '')
	comment_preview.short_description = 'Comment'
	
	def like_type(self, obj):
		return '👍 Like' if obj.is_like else '👎 Dislike'
	like_type.short_description = 'Type'

@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ('tag', 'sender_name', 'sender_email', 'subject', 'sent_at', 'status')
    list_filter = ('tag', 'status', 'sent_at')
    search_fields = ('sender_name', 'sender_email', 'subject', 'message')