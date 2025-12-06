from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, FileResponse
from .models import Trip, Booking, ChatMessage, UserProfile, TeamMember, GalleryImage, Like, Comment, CommentLike
from .forms import ContactForm
from .locations import KENYA_LOCATIONS
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.core.mail import EmailMessage, BadHeaderError
from django.contrib import messages
import logging, time
from django.conf import settings
from .models import SentEmail
from django.http import HttpResponse

logger = logging.getLogger(__name__)

# Home page
def home(request):
    return render(request, "index.html")

# Trips landing page (after login)
@login_required
def trips(request):
    # Get filter parameter from URL (upcoming, success, cancelled, all)
    status_filter = request.GET.get('status', 'all')
    
    if status_filter == 'all':
        trip_list = Trip.objects.all()
    else:
        trip_list = Trip.objects.filter(status=status_filter)
    
    return render(request, "destinations.html", {
        "trips": trip_list,
        "status_filter": status_filter
    })

# Trip detail page
@login_required
def trip_details(request, id):
    trip = get_object_or_404(Trip, id=id)
    return render(request, "trip_details.html", {"trip": trip})

# Book a trip
@login_required
def book_trip(request, id):
    trip = get_object_or_404(Trip, id=id)
    Booking.objects.create(user=request.user, trip=trip)
    return redirect("trips")

# Contact us page
def contact_us(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', 'No Subject')
        message = request.POST.get('message', '')
        from_email = request.POST.get('email', '')

        if not subject or not message or not from_email:
            messages.error(request, 'All fields are required.')
            return render(request, 'contact_us.html')
        
        email = EmailMessage(
            subject,
            message,
            from_email,
            ['centraladventurers@gmail.com']
        )

        max_retries = 3
        for attempt in range(1, max_retries +1):
            try:
                email.send(fail_silently=False)
                messages.success(request, 'Email sent successfully.')
                logger.info(f"Contact email sent from {from_email} with subject '{subject}'")
                break
            except BadHeaderError:
                messages.error(request, 'Invalid header found.')
                logger.error(f"BadHeaderError when sending contact email from {from_email}")
                break
            except Exception as e:
                logger.exception(f"Error sending contact email from {from_email}, attempt {attempt}: {e}")
                if attempt < max_retries:
                    time.sleep(2 **attempt)
                else:
                    messages.error(request, 'Failed to send email after multiple attempts.')
        return redirect('contact_us')
    
    return render(request, "contact_us.html")
# Group chat page
@login_required
def chat_room(request):
    # If you have a dedicated chat template create `chat.html` in templates;
    # fall back to the notification demo for now if it's present.
    try:
        return render(request, "chat.html")
    except Exception:
        return render(request, "notification-demo.html")

# Simple views to render the static frontend templates that live under
# `trips/templates/` so they are reachable via URL routes.
def login_page(request):
    # Handle login POST - accept username or email
    if request.method == 'POST':
        identifier = request.POST.get('email')
        password = request.POST.get('password')

        user = None
        # Try by username first
        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                user = None

        if user is None:
            messages.error(request, 'User not found.')
            return render(request, 'login.html')

        user_auth = authenticate(request, username=user.username, password=password)
        if user_auth is not None:
            login(request, user_auth)
            messages.success(request, 'Logged in successfully.')
            return redirect('trips')
        else:
            messages.error(request, 'Invalid credentials.')
            return render(request, 'login.html')

    return render(request, "login.html")

def signup_page(request):
    # Handle signup form POST to create a User and UserProfile
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirmPassword')
        first_name = request.POST.get('firstName', '')
        last_name = request.POST.get('lastName', '')
        age = request.POST.get('age')
        county = request.POST.get('county', '')
        constituency = request.POST.get('constituency', '')
        bio = request.POST.get('bio', '')
        contact_info = request.POST.get('contactInfo', '')

        if not username or not email or not password:
            messages.error(request, 'Username, email and password are required.')
            return render(request, 'signup.html')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Create profile
        profile = UserProfile.objects.create(
            user=user,
            age=int(age) if age else None,
            county=county,
            constituency=constituency,
            bio=bio,
            contact_info=contact_info
        )

        # Optionally authenticate and login the new user
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Account created and logged in.')
            return redirect('trips')

        return redirect('login')

    return render(request, "signup.html")

@login_required
def gallery_page(request):
    from .models import GalleryImage
    gallery_images = GalleryImage.objects.all().order_by('-id')
    return render(request, "gallery.html", {"gallery_images": gallery_images})

def edit_profile_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update user fields
        username = request.POST.get('username')
        first_name = request.POST.get('firstName', '')
        last_name = request.POST.get('lastName', '')
        email = request.POST.get('email', '')

        if username and username != request.user.username:
            if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
                messages.error(request, 'Username already taken.')
                return redirect('edit_profile')
            request.user.username = username

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        # Update profile fields
        age = request.POST.get('age')
        county = request.POST.get('county', '')
        constituency = request.POST.get('constituency', '')
        bio = request.POST.get('bio', '')
        contact_info = request.POST.get('contactInfo', '')
        profile.age = int(age) if age else None
        profile.county = county
        profile.constituency = constituency
        profile.bio = bio
        profile.contact_info = contact_info

        # Handle uploaded profile picture with basic validation
        uploaded_image = request.FILES.get('profile_picture')
        if uploaded_image:
            # Basic server-side validation: limit size and ensure image content type
            max_bytes = 2 * 1024 * 1024  # 2 MB
            content_type = uploaded_image.content_type
            if uploaded_image.size > max_bytes:
                messages.error(request, 'Image too large. Maximum size is 2MB.')
                return redirect('edit_profile')
            if not content_type.startswith('image/'):
                messages.error(request, 'Invalid file type. Please upload an image.')
                return redirect('edit_profile')

            profile.profile_picture = uploaded_image
        profile.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('trips')

    # GET - prefill form
    context = {
        'user': request.user,
        'profile': profile,
    }
    return render(request, "edit-profile.html", context)

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

def destinations_page(request):
    return render(request, "destinations.html")

def notification_demo(request):
    return render(request, "notification-demo.html")
from django.utils import timezone
from .models import Booking

def remove_unpaid_bookings():
    now = timezone.now()
    unpaid_bookings = Booking.objects.filter(deposit_paid=False, pay_later_deadline__lt=now)
    for booking in unpaid_bookings:
        booking.delete()


# API endpoints for location data
def api_counties(request):
    """Return list of all Kenyan counties."""
    counties = sorted(KENYA_LOCATIONS.keys())
    return JsonResponse({'counties': counties})


def api_constituencies(request):
    """Return constituencies for a given county."""
    county = request.GET.get('county', '')
    if county and county in KENYA_LOCATIONS:
        constituencies = KENYA_LOCATIONS[county]
        return JsonResponse({'constituencies': constituencies})
    return JsonResponse({'constituencies': [], 'error': 'County not found'}, status=400)


# Management/Leadership page
def management_page(request):
    """Display team members and leadership."""
    team_members = TeamMember.objects.all()
    return render(request, 'management.html', {'team_members': team_members})


# Gallery Like/Unlike
@login_required
def toggle_like(request, image_id):
    """Toggle like on a gallery image"""
    if request.method == 'POST':
        image = get_object_or_404(GalleryImage, id=image_id)
        like, created = Like.objects.get_or_create(user=request.user, image=image)
        
        if not created:
            # Unlike
            like.delete()
            is_liked = False
        else:
            # Like
            is_liked = True
        
        like_count = image.likes.count()
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'like_count': like_count
        })
    return JsonResponse({'success': False}, status=400)


# Gallery Add Comment
@login_required
def add_comment(request, image_id):
    """Add comment to gallery image"""
    if request.method == 'POST':
        image = get_object_or_404(GalleryImage, id=image_id)
        comment_text = request.POST.get('comment', '').strip()
        
        if comment_text:
            comment = Comment.objects.create(
                user=request.user,
                image=image,
                comment=comment_text
            )
            return JsonResponse({
                'success': True,
                'comment_id': comment.id,
                'username': comment.user.username,
                'avatar': comment.user.profile.profile_picture.url if hasattr(comment.user, 'profile') and comment.user.profile.profile_picture else '',
                'comment_text': comment.comment,
                'time': comment.time.strftime('%b %d, %Y %H:%M')
            })
        else:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)
    
    return JsonResponse({'success': False}, status=400)


# Gallery Download Media
@login_required
def download_media(request, image_id):
    """Download image or video from gallery"""
    image = get_object_or_404(GalleryImage, id=image_id)
    
    if image.media_type == 'image' and image.image_url:
        file_path = image.image_url.path
        filename = f"{image.trip.title}_{image.id}.jpg"
    elif image.media_type == 'video' and image.video_url:
        file_path = image.video_url.path
        filename = f"{image.trip.title}_{image.id}.mp4"
    else:
        return JsonResponse({'error': 'Media file not found'}, status=404)
    
    try:
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except FileNotFoundError:
        return JsonResponse({'error': 'File not found'}, status=404)


# Gallery Get Comments
@login_required
def get_comments(request, image_id):
    """Get all comments for a gallery image"""
    image = get_object_or_404(GalleryImage, id=image_id)
    comments = image.comments.filter(parent_comment__isnull=True)  # Get top-level comments only
    
    comments_data = []
    for comment in comments:
        avatar = ''
        if hasattr(comment.user, 'profile') and comment.user.profile.profile_picture:
            avatar = comment.user.profile.profile_picture.url
        
        # Get comment likes/dislikes
        likes = comment.likes.filter(is_like=True).count()
        dislikes = comment.likes.filter(is_like=False).count()
        user_like = comment.likes.filter(user=request.user).first()
        user_like_status = None
        if user_like:
            user_like_status = 'like' if user_like.is_like else 'dislike'
        
        # Get replies
        replies_data = []
        for reply in comment.replies.all():
            reply_avatar = ''
            if hasattr(reply.user, 'profile') and reply.user.profile.profile_picture:
                reply_avatar = reply.user.profile.profile_picture.url
            
            reply_likes = reply.likes.filter(is_like=True).count()
            reply_dislikes = reply.likes.filter(is_like=False).count()
            
            replies_data.append({
                'id': reply.id,
                'username': reply.user.username,
                'avatar': reply_avatar,
                'comment': reply.comment,
                'time': reply.time.strftime('%b %d, %Y %H:%M'),
                'is_owner': reply.user == request.user,
                'likes': reply_likes,
                'dislikes': reply_dislikes
            })
        
        comments_data.append({
            'id': comment.id,
            'username': comment.user.username,
            'avatar': avatar,
            'comment': comment.comment,
            'time': comment.time.strftime('%b %d, %Y %H:%M'),
            'is_owner': comment.user == request.user,
            'likes': likes,
            'dislikes': dislikes,
            'user_like_status': user_like_status,
            'replies': replies_data
        })
    
    return JsonResponse({'comments': comments_data})


# Delete Comment
@login_required
def delete_comment(request, comment_id):
    """Delete a comment (only comment owner or admin)"""
    if request.method == 'DELETE':
        comment = get_object_or_404(Comment, id=comment_id)
        
        if comment.user != request.user and not request.user.is_staff:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        comment.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)


# Edit Comment
@login_required
def edit_comment(request, comment_id):
    """Edit a comment (only comment owner)"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        
        if comment.user != request.user:
            return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
        new_text = request.POST.get('comment', '').strip()
        if not new_text:
            return JsonResponse({'success': False, 'error': 'Comment cannot be empty'}, status=400)
        
        comment.comment = new_text
        comment.save()
        
        return JsonResponse({
            'success': True,
            'comment': new_text,
            'time': comment.time.strftime('%b %d, %Y %H:%M')
        })
    
    return JsonResponse({'success': False}, status=400)


# Reply to Comment
@login_required
def reply_comment(request, comment_id):
    """Add reply to a comment"""
    if request.method == 'POST':
        parent = get_object_or_404(Comment, id=comment_id)
        reply_text = request.POST.get('comment', '').strip()
        
        if not reply_text:
            return JsonResponse({'success': False, 'error': 'Reply cannot be empty'}, status=400)
        
        reply = Comment.objects.create(
            user=request.user,
            image=parent.image,
            comment=reply_text,
            parent_comment=parent
        )
        
        avatar = ''
        if hasattr(reply.user, 'profile') and reply.user.profile.profile_picture:
            avatar = reply.user.profile.profile_picture.url
        
        return JsonResponse({
            'success': True,
            'reply_id': reply.id,
            'username': reply.user.username,
            'avatar': avatar,
            'comment': reply.comment,
            'time': reply.time.strftime('%b %d, %Y %H:%M')
        })
    
    return JsonResponse({'success': False}, status=400)


# Like/Dislike Comment
@login_required
def toggle_comment_like(request, comment_id):
    """Toggle like/dislike on a comment"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        is_like = request.POST.get('is_like', 'true').lower() == 'true'
        
        like, created = CommentLike.objects.get_or_create(
            user=request.user,
            comment=comment,
            defaults={'is_like': is_like}
        )
        
        if not created:
            # Toggle or remove
            if like.is_like == is_like:
                # Same action, remove it
                like.delete()
                status = None
            else:
                # Different action, update it
                like.is_like = is_like
                like.save()
                status = 'like' if is_like else 'dislike'
        else:
            status = 'like' if is_like else 'dislike'
        
        likes = comment.likes.filter(is_like=True).count()
        dislikes = comment.likes.filter(is_like=False).count()
        
        return JsonResponse({
            'success': True,
            'likes': likes,
            'dislikes': dislikes,
            'user_like_status': status
        })
    
    return JsonResponse({'success': False}, status=400)
