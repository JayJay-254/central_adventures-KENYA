from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, FileResponse
from .models import Trip, Booking, ChatMessage, UserProfile, TeamMember, GalleryImage, Like, Comment, CommentLike
from django.views.decorators.csrf import csrf_exempt
from .forms import ContactForm
from .locations import KENYA_LOCATIONS
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.core.mail import EmailMessage, BadHeaderError, send_mail
from django.contrib import messages
import logging, time
from django.conf import settings
from .models import SentEmail
from django.http import HttpResponse
import requests
from base64 import b64encode
from datetime import datetime, timedelta
from trips.models import Trip
from django.views.decorators.csrf import csrf_exempt
import json
from decimal import Decimal

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

    if request.method == 'POST':
        payment_number = request.POST.get('payment_number')
        payment_amount = request.POST.get('payment_amount')

        if not payment_number or not payment_amount:
            messages.error(request, 'Payment number and amount are required.')
            return redirect('trip_details', id=id)

        booking = Booking.objects.create(
            user=request.user,
            trip=trip,
            paid=False,
            deposit_paid=False,
            approved=False
        )

        # Save payment details (optional: create a Payment model if needed)
        booking.payment_number = payment_number
        booking.payment_amount = payment_amount
        booking.save()

        messages.success(request, 'Booking request submitted. Awaiting admin approval.')
        return redirect('trips')

    return render(request, "trip_details.html", {"trip": trip})

# Admin approval for bookings
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            booking.approved = True
            booking.save()

            # Notify the user
            send_mail(
                'Booking Approved',
                f'Your seat is now reserved for the trip to {booking.trip.title}.',
                'admin@centraladventures.com',
                [booking.user.email],
                fail_silently=False,
            )
            messages.success(request, 'Booking approved and user notified.')
        elif action == 'decline':
            booking.delete()

            # Notify the user
            send_mail(
                'Booking Declined',
                f'Your booking for the trip to {booking.trip.title} was declined.',
                'admin@centraladventures.com',
                [booking.user.email],
                fail_silently=False,
            )
            messages.success(request, 'Booking declined and user notified.')

        return redirect('admin_dashboard')

    return render(request, 'admin_booking_approval.html', {"booking": booking})

# Contact us page
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for reaching out! Your message has been sent.')
            return redirect('contact_us')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()

    return render(request, "contacts.html", {"form": form})

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
@csrf_exempt
def toggle_like(request, image_id):
    image = get_object_or_404(GalleryImage, id=image_id)
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Like for authenticated users
        if user:
            like, created = Like.objects.get_or_create(user=user, image=image)
            if not created:
                like.delete()
                is_liked = False
            else:
                is_liked = True
        else:  # Guest user like using session
            like, created = Like.objects.get_or_create(session_key=session_key, image=image)
            if not created:
                like.delete()
                is_liked = False
            else:
                is_liked = True

        return JsonResponse({'success': True, 'is_liked': is_liked, 'like_count': image.likes.count()})

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
    comments = image.comments.filter(parent_comment__isnull=True)

    comments_data = []
    for comment in comments:

        avatar = ''
        if hasattr(comment.user, 'profile') and comment.user.profile.profile_picture:
            avatar = comment.user.profile.profile_picture.url

        likes = comment.likes.filter(is_like=True).count()
        dislikes = comment.likes.filter(is_like=False).count()

        user_like = comment.likes.filter(user=request.user).first()
        user_like_status = None
        if user_like:
            user_like_status = 'like' if user_like.is_like else 'dislike'

        # Replies
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

    # Final return (no comma!)
    return JsonResponse({
        'success': True,
        'comments': comments_data
    })

@login_required
def add_comment(request, image_id):
    if request.method == "POST":
        logger.debug(f"Incoming POST data: {request.POST}")
        # Ensure the text field is provided and not empty
        text = request.POST.get("text", "").strip()
        if not text:
            return JsonResponse({"status": "error", "message": "Comment text cannot be empty."}, status=400)

        image = get_object_or_404(GalleryImage, id=image_id)

        # Create the comment
        comment = Comment.objects.create(
            image=image,
            user=request.user,
            comment=text
        )

        # Return the created comment data
        return JsonResponse({
            "status": "success",
            "comment": {
                "id": comment.id,
                "username": comment.user.username,
                "comment": comment.comment,
                "time": comment.time.strftime('%b %d, %Y %H:%M'),
                "likes": 0,
                "dislikes": 0,
                "replies": []
            }
        })


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

def get_mpesa_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    return response.json()['access_token']


from decimal import Decimal

def payment_page(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == "POST":
        phone = request.POST.get("phone")

        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('+'):
            phone = phone[1:]
        amount = int(trip.price)  # convert Decimal to int

        # Create initial booking
        booking = Booking.objects.create(
            user=request.user,
            trip=trip,
            phone=phone,
            amount=amount,
            status="pending"
        )

        try:
            access_token = get_mpesa_token()
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = b64encode(f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}".encode()).decode()

            stk_request = {
                "BusinessShortCode": settings.MPESA_SHORTCODE,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone,
                "PartyB": settings.MPESA_SHORTCODE,
                "PhoneNumber": phone,
                "CallBackURL": settings.MPESA_CALLBACK_URL,
                "AccountReference": f"TRIP-{trip_id}",
                "TransactionDesc": f"Payment for {trip.title}"
            }

            headers = {"Authorization": f"Bearer {access_token}"}

            response = requests.post(
                "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                json=stk_request,
                headers=headers,
                timeout=10
            )

            data = response.json()

            if data.get("ResponseCode") == "0":
                message = "STK Push sent! Enter your M-Pesa PIN to complete payment."
            else:
                message = f"Payment request failed: {data.get('errorMessage', 'Unknown error')}"

        except requests.exceptions.RequestException as e:
            message = f"Payment request failed: {str(e)}"

        return render(request, "payment_page.html", {"trip": trip, "message": message})

    return render(request, "payment_page.html", {"trip": trip})
@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body.decode("utf-8"))

    result = data["Body"]["stkCallback"]["ResultCode"]
    meta = data["Body"]["stkCallback"].get("CallbackMetadata", {})

    if result == 0:  # Payment successful
        items = meta["Item"]
        receipt = [x["Value"] for x in items if x["Name"] == "MpesaReceiptNumber"][0]
        amount = [x["Value"] for x in items if x["Name"] == "Amount"][0]
        phone = [x["Value"] for x in items if x["Name"] == "PhoneNumber"][0]

        booking = Booking.objects.get(phone=str(phone), amount=amount, status="pending")
        booking.status = "paid"
        booking.mpesa_receipt = receipt
        booking.save()

    return JsonResponse({"status": "ok"})