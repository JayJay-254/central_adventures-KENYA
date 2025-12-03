from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta


def default_pay_later_deadline():
    return timezone.now() + timedelta(days=7)

# Trip categories
class TripCategory(models.Model):
    name = models.CharField(max_length=50)

# Trips
class Trip(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('success', 'Successful'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.ForeignKey(TripCategory, on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    date = models.DateField()
    image_url = models.CharField(max_length=500)
    description_short = models.CharField(max_length=255)
    description_full = models.TextField()
    featured = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')

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
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    image_url = models.ImageField(upload_to='gallery/', null=True, blank=True)
    caption = models.TextField()
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

# Likes
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE)

# Comments
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(GalleryImage, on_delete=models.CASCADE)
    comment = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

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
