from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta


def default_pay_later_deadline():
    return timezone.now() + timedelta(days=7)

# Trip categories
class TripCategory(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name


# Trip Types
class TripType(models.Model):
    TYPE_CHOICES = [
        ('short_trip', 'Short Trip'),
        ('medium_trip', 'Medium Trip'),
        ('mega_trip', 'Mega Trip'),
    ]
    name = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    description = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.get_name_display()


# Trips
class Trip(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('success', 'Successful'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.ForeignKey(TripCategory, on_delete=models.CASCADE)
    trip_type = models.ForeignKey(TripType, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=200)
    date = models.DateField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image_url = models.ImageField(upload_to='trips/', null=True, blank=True)
    description_short = models.CharField(max_length=255)
    description_full = models.TextField()
    featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    
    def get_duration_display(self):
        """Return duration as 'X nights Y days' format"""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            days = delta.days
            nights = max(0, days - 1) if days > 0 else 0
            if days > 0:
                return f"{nights} nights {days} days"
        return "TBD"
    
    def __str__(self):
        return self.title

# Bookings
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    deposit_paid = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    book_date = models.DateTimeField(auto_now_add=True)
    pay_later_deadline = models.DateTimeField(default=default_pay_later_deadline)

# Admin Roles
class AdminRole(models.Model):
    ROLE_CHOICES = [
        ("chairman", "Chairman"),
        ("secretary", "Secretary"),
        ("treasurer", "Treasurer"),
        ("org_sec", "Organizing Secretary"),
        ("it_dept", "IT Department")
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

# Gallery Images
class GalleryImage(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    image_url = models.ImageField(upload_to='gallery/', null=True, blank=True)
    video_url = models.FileField(upload_to='gallery/videos/', null=True, blank=True)
    caption = models.TextField()
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.trip.title} - {self.get_media_type_display()}"
    
    def is_image(self):
        return self.media_type == 'image'
    
    def is_video(self):
        return self.media_type == 'video'

# Likes
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'image')
    
    def __str__(self):
        return f"{self.user.username} likes {self.image}"

# Comments
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['-time']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.image}"
    
    def is_reply(self):
        return self.parent_comment is not None


# Comment Likes
class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    is_like = models.BooleanField(default=True)  # True = like/thumbs up, False = dislike/thumbs down
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'comment')
    
    def __str__(self):
        return f"{self.user.username} {'likes' if self.is_like else 'dislikes'} comment {self.comment.id}"

# Group Chat
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

# Contact Us Form
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)


# Team/Management
class TeamMember(models.Model):
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    image = models.ImageField(upload_to='team/', null=True, blank=True)
    contact = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.position}"


# Optional user profile for storing extra signup details
class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    age = models.PositiveIntegerField(null=True, blank=True)
    county = models.CharField(max_length=100, blank=True)
    constituency = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    contact_info = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"
